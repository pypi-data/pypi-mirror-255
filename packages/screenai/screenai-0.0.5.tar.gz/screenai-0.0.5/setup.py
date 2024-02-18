# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['screenai']

package_data = \
{'': ['*']}

install_requires = \
['einops', 'swarms', 'torch', 'torchvision', 'zetascale']

setup_kwargs = {
    'name': 'screenai',
    'version': '0.0.5',
    'description': 'Screen AI - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# Screen AI\nImplementation of the ScreenAI model from the paper: "A Vision-Language Model for UI and Infographics Understanding". The flow is:\nimg + text -> patch sizes -> vit -> embed + concat -> attn + ffn -> cross attn + ffn + self attn -> to out. [PAPER LINK: ](https://arxiv.org/abs/2402.04615)\n\n## Install\n`pip3 install screenai`\n\n## Usage\n```python\n\nimport torch\nfrom screenai.main import ScreenAI\n\n# Create a tensor for the image\nimage = torch.rand(1, 3, 224, 224)\n\n# Create a tensor for the text\ntext = torch.randn(1, 1, 512)\n\n# Create an instance of the ScreenAI model with specified parameters\nmodel = ScreenAI(\n    patch_size=16,\n    image_size=224,\n    dim=512,\n    depth=6,\n    heads=8,\n    vit_depth=4,\n    multi_modal_encoder_depth=4,\n    llm_decoder_depth=4,\n    mm_encoder_ff_mult=4,\n)\n\n# Perform forward pass of the model with the given text and image tensors\nout = model(text, image)\n\n# Print the shape of the output tensor\nprint(out)\n\n\n```\n\n# License\nMIT\n\n\n## Citation\n```bibtex\n\n@misc{baechler2024screenai,\n    title={ScreenAI: A Vision-Language Model for UI and Infographics Understanding}, \n    author={Gilles Baechler and Srinivas Sunkara and Maria Wang and Fedir Zubach and Hassan Mansoor and Vincent Etter and Victor Cărbune and Jason Lin and Jindong Chen and Abhanshu Sharma},\n    year={2024},\n    eprint={2402.04615},\n    archivePrefix={arXiv},\n    primaryClass={cs.CV}\n}\n```',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/ScreenAI',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
