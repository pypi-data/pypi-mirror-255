MODEL_TYPE_CHOICES = ['huggingface', 'replicate', 'octo']
MODEL_NAMES_MAPPING = {
    'huggingface': ['gpt2', 'bigscience/bloom-560m', 'other'],
    'replicate': ['replicate/llama-7b', 'replicate/llama-13b-lora', 'other'],
    'octo': ['llama-2-7b-chat', 'other'],
}
PROBES_CHOICES = ['security', 'toxicity', 'hallucination', 'ethics']
PROBES_DIMENSIONS_MAPPING = {
    'security': 'dan,encoding,gcg,glitch,knownbadsignatures,leakerplay,malwaregen,packagehallucination,promptinject,xss',
    'toxicity': 'atkgen,continuation,realtoxicityprompts',
    'hallucination': 'goodside,snowball,misleading,packagehallucination',
    'ethics': 'lmrc',
}
DTYPE_CHOICES = ['local', 'private', 'public']

MODEL_TYPE_MAPPING = {
    'huggingface': 'HF',
    'replicate': 'Replicate',
    'octo': 'Octo'
}