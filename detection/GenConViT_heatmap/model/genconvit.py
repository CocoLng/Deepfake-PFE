# genconvit.py
import torch
import torch.nn as nn
from .genconvit_ed import GenConViTED
from .genconvit_vae import GenConViTVAE

class GenConViT(nn.Module):
    def __init__(self, config, ed, vae, net, fp16):
        super(GenConViT, self).__init__()
        self.net = net
        self.fp16 = fp16

        # init the ED model
        self.model_ed = GenConViTED(config)
        checkpoint_ed = torch.load(f'weight/{ed}.pth', map_location='cpu')
        if 'state_dict' in checkpoint_ed:
            self.model_ed.load_state_dict(checkpoint_ed['state_dict'])
        else:
            self.model_ed.load_state_dict(checkpoint_ed)
        self.model_ed.eval()
        if self.fp16:
            self.model_ed.half()

        # init the VAE model
        self.model_vae = GenConViTVAE(config)
        checkpoint_vae = torch.load(f'weight/{vae}.pth', map_location='cpu')
        if 'state_dict' in checkpoint_vae:
            self.model_vae.load_state_dict(checkpoint_vae['state_dict'])
        else:
            self.model_vae.load_state_dict(checkpoint_vae)
        self.model_vae.eval()
        if self.fp16:
            self.model_vae.half()

    def forward(self, x):
        """Return classification logits & some reconstruction depending on net."""
        if self.net == 'ed':
            # Just ED
            logits, decimg = self.model_ed(x)  # shape [N,2], [N,3,224,224]
            return logits, decimg
        elif self.net == 'vae':
            # Just VAE
            logits, decimg = self.model_vae(x) # shape [N,2], [N,3,224,224]
            return logits, decimg
        else:
            # net='genconvit' => combine ED and VAE
            logits_ed, dec_ed = self.model_ed(x)
            logits_vae, dec_vae = self.model_vae(x)

            # For classification, average the two logits => shape [N,2]
            combined_logits = (logits_ed + logits_vae) / 2

            # For reconstruction, pick one. We'll pick ED's dec for example:
            combined_decimg = dec_ed

            return combined_logits, combined_decimg
