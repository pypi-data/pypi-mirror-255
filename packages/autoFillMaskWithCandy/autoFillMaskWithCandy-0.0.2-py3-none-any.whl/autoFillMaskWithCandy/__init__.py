"""
My NLP Package
This package provides functionalities for processing and comparing sentences
using models from Hugging Face's Transformers library.
"""

__version__ = '0.0.2'

from .autoFillMaskWithCandy import setTokenModel, mask_differing_words, show_mask_fill, mask_fill_replaced
