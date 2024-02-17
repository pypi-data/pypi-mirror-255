from typing import Optional

import numpy as np
from tqdm import tqdm
from PIL import Image
import torch
from torch import autocast
from transformers import CLIPTextModel, CLIPTokenizer
from transformers import DPTForDepthEstimation, DPTFeatureExtractor
from diffusers import AutoencoderKL, UNet2DConditionModel
from diffusers.schedulers.scheduling_pndm import PNDMScheduler
from .depth_to_image_pipeline import Depth2ImageEnhancerPipeline


class DiffusionPipeline:
    def __init__(self,
                 vae,
                 tokenizer,
                 text_encoder,
                 unet,
                 scheduler):

        self.vae = vae
        self.tokenizer = tokenizer
        self.text_encoder = text_encoder
        self.unet = unet
        self.scheduler = scheduler
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def get_text_embeds(self, text):
        # tokenize the text
        text_input = self.tokenizer(
            text,
            padding="max_length",
            max_length=self.tokenizer.model_max_length,
            truncation=True,
            return_tensors="pt"
        )
        # embed the text
        with torch.no_grad():
            text_embeds = self.text_encoder(text_input.input_ids.to(self.device))[0]
        return text_embeds

    def get_prompt_embeds(self, prompt):
        if isinstance(prompt, str):
            prompt = [prompt]
        cond_embeds = self.get_text_embeds(prompt)
        un_cond_embeds = self.get_text_embeds([""] * len(prompt))

        prompt_embeds = torch.cat([un_cond_embeds, cond_embeds])
        return prompt_embeds

    def decode_img_latents(self, img_latents):
        img_latents = 1 / self.vae.config.scaling_factor * img_latents
        with torch.no_grad():
            img = self.vae.decode(img_latents).sample

        img = (img / 2 + 0.5).clamp(0, 1)
        img = img.cpu().permute(0, 2, 3, 1).float().numpy()
        return img

    @staticmethod
    def transform_img(img):
        img = (img * 255).round().astype("uint8")
        img = [Image.fromarray(i) for i in img]
        return img

    def encode_img_latents(self, img, latent_timestep):
        if not isinstance(img, list):
            img = [img]
        img = 2 * ((np.stack([np.array(i) for i in img], axis=0) / 255.0) - 0.5)
        img = torch.from_numpy(img).float().permute(0, 3, 1, 2)
        img_latents = self.vae.config.scaling_factor * self.vae.encode(img.to(self.device)).latent_dist.sample()
        noise = torch.randn(img_latents.shape).to(self.device)
        img_latents = self.scheduler.add_noise(img_latents, noise, latent_timestep)
        return img_latents


class Depth2ImgPipeline(DiffusionPipeline):
    def __init__(
            self,
            vae,
            tokenizer,
            text_encoder,
            unet,
            scheduler,
            depth_feature_extractor,
            depth_estimator
    ):
        super().__init__(vae, tokenizer, text_encoder, unet, scheduler)
        self.depth_feature_extractor = depth_feature_extractor
        self.depth_estimator = depth_estimator

    def get_depth_mask(self, img):
        if not isinstance(img, list):
            img = [img]
        width, height = img[0].size
        # pre-process the input image and get its pixel values
        pixel_values = self.depth_feature_extractor(img, return_tensors="pt").pixel_values
        # use autocast for automatic mixed precision (AMP) inference
        with autocast("cuda"):
            depth_mask = self.depth_estimator(pixel_values).predicted_depth
        # get the depth mask
        depth_mask = torch.nn.functional.interpolate(
            depth_mask.unsqueeze(1),
            size=(height // 8, width // 8),
            mode="bicubic",
            align_corners=False
        )
        # scale the mask to range [-1, 1]
        depth_min = torch.amin(depth_mask, dim=[1, 2, 3], keepdim=True)
        depth_max = torch.amax(depth_mask, dim=[1, 2, 3], keepdim=True)
        depth_mask = 2.0 * (depth_mask - depth_min) / (depth_max - depth_min) - 1.0
        depth_mask = depth_mask.to(self.device)
        # replicate the mask for classifier free guidance 
        depth_mask = torch.cat([depth_mask] * 2)
        return depth_mask

    def denoise_latents(
            self,
            img,
            prompt_embeds,
            depth_mask,
            strength,
            num_inference_steps=50,
            guidance_scale=7.5,
            height=512,
            width=512,
            **kwargs
    ):
        strength = max(min(strength, 1), 0)
        self.scheduler.set_timesteps(num_inference_steps)
        init_timestep = int(num_inference_steps * strength)
        t_start = num_inference_steps - init_timestep
        time_steps = self.scheduler.timesteps[t_start:]
        num_inference_steps = num_inference_steps - t_start
        latent_timestep = time_steps[:1].repeat(1)
        latents = self.encode_img_latents(img, latent_timestep)
        with autocast("cuda"):
            for i, t in tqdm(enumerate(time_steps)):
                latent_model_input = torch.cat([latents] * 2)
                latent_model_input = torch.cat([latent_model_input, depth_mask], dim=1)
                with torch.no_grad():
                    noise_pred = self.unet(latent_model_input, t, encoder_hidden_states=prompt_embeds)["sample"]
                noise_pred_un_cond, noise_pred_text = noise_pred.chunk(2)
                noise_pred = noise_pred_un_cond + guidance_scale * (noise_pred_text - noise_pred_un_cond)
                latents = self.scheduler.step(noise_pred, t, latents)["prev_sample"]
        return latents

    def __call__(
            self,
            prompt,
            img,
            strength=0.8,
            num_inference_steps=50,
            guidance_scale=7.5,
            height=512, width=512
    ):
        prompt_embeds = self.get_prompt_embeds(prompt)
        depth_mask = self.get_depth_mask(img)
        latents = self.denoise_latents(
            img,
            prompt_embeds,
            depth_mask,
            strength,
            num_inference_steps,
            guidance_scale,
            height,
            width
        )
        img = self.decode_img_latents(latents)
        img = self.transform_img(img)
        return img


class ImageTextToImageAlgoEnhancer:
    def __init__(
            self,
            huggingface_repo_id: str,
            vae_huggingface_repo_id: Optional[str] = None,
            tokenizer_huggingface_repo_id: Optional[str] = None,
            text_encoder_huggingface_repo_id: Optional[str] = None,
            unet_huggingface_repo_id: Optional[str] = None,
            depth_estimator_huggingface_repo_id: Optional[str] = None,
            depth_feature_extractor_huggingface_repo_id: Optional[str] = None,
            beta_start: float = 0.00085,
            beta_end: float = 0.012,
            beta_schedule: str = "scaled_linear",
            num_train_timesteps: int = 1000,
            device_map="auto",
            torch_dtype=torch.float16
    ):
        scheduler = PNDMScheduler(
            beta_start=beta_start,
            beta_end=beta_end,
            beta_schedule=beta_schedule,
            num_train_timesteps=num_train_timesteps
        )

        self.scheduler = scheduler
        self.huggingface_repo_id = huggingface_repo_id
        self.vae_huggingface_repo_id = vae_huggingface_repo_id or huggingface_repo_id
        self.tokenizer_huggingface_repo_id = tokenizer_huggingface_repo_id or huggingface_repo_id
        self.text_encoder_huggingface_repo_id = text_encoder_huggingface_repo_id or huggingface_repo_id
        self.unet_huggingface_repo_id = unet_huggingface_repo_id or huggingface_repo_id
        self.depth_estimator_huggingface_repo_id = depth_estimator_huggingface_repo_id or huggingface_repo_id
        self.depth_feature_extractor_huggingface_repo_id = (
                depth_feature_extractor_huggingface_repo_id or huggingface_repo_id
        )
        self.pipe = None
        self.is_static_pipeline = None
        self.device_map = device_map
        self.torch_dtype = torch_dtype

    def create_static_pipeline(
            self,
            device: str
    ):
        vae = AutoencoderKL.from_pretrained(
            self.vae_huggingface_repo_id,
            subfolder="vae"
        ).to(device)
        tokenizer = CLIPTokenizer.from_pretrained(
            self.tokenizer_huggingface_repo_id,
            subfolder="tokenizer"
        )
        text_encoder = CLIPTextModel.from_pretrained(
            self.text_encoder_huggingface_repo_id,
            subfolder="text_encoder"
        ).to(device)
        unet = UNet2DConditionModel.from_pretrained(
            self.unet_huggingface_repo_id,
            subfolder="unet"
        ).to(device)

        depth_estimator = DPTForDepthEstimation.from_pretrained(
            self.depth_estimator_huggingface_repo_id,
            subfolder="depth_estimator"
        )
        # Load DPT Feature Extractor
        depth_feature_extractor = DPTFeatureExtractor.from_pretrained(
            self.depth_feature_extractor_huggingface_repo_id,
            subfolder="feature_extractor"
        )
        self.is_static_pipeline = True
        self.pipe = Depth2ImgPipeline(
            vae,
            tokenizer,
            text_encoder,
            unet,
            self.scheduler,
            depth_feature_extractor,
            depth_estimator
        )

    def create_dynamic_pipeline(self):
        self.is_static_pipeline = False
        self.pipe = Depth2ImageEnhancerPipeline.from_pretrained(
            self.huggingface_repo_id,
            device_map=self.device_map,
            torch_dtype=self.torch_dtype
        )

    def ready(self):
        return self.pipe is not None and self.is_static_pipeline is not None
