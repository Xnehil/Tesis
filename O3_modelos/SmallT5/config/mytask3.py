import functools
import seqio
import t5.data
from t5.data import preprocessors
import tensorflow as tf
TaskRegistry = seqio.TaskRegistry
MixtureRegistry = seqio.MixtureRegistry 


vocab='tokenizadorIskonawa.model'
#vocab='/home/mulcar/roberta/slovene/transformers_epoch98/sentencepiece.bpe.model'
#datasplit = {'train': '/home/mulcar/text-to-text-transfer-transformer/t5/mydata/sl_corpora_all.t5.train.tsv', 'validation': '/home/mulcar/text-to-text-transfer-transformer/t5/mydata/sl_corpora_all.t5.eval.tsv'}
datasplit = {
    "train": "iskCorpus.t5.train.tsv",
    "validation": "iskCorpus.t5.eval.tsv"
}

DEFAULT_OUTPUT_FEATURES = {
    "inputs": seqio.Feature(
        seqio.SentencePieceVocabulary(vocab), add_eos=True,
        required=False, dtype=tf.int32),
    "targets": seqio.Feature(
        seqio.SentencePieceVocabulary(vocab), add_eos=True, dtype=tf.int32)
}
TaskRegistry.add(
    "iskonawa_span_corruption",
    source=seqio.TextLineDataSource(split_to_filepattern=datasplit),
    preprocessors=[
        functools.partial(
            preprocessors.parse_tsv),
        seqio.preprocessors.tokenize,
        #seqio.CacheDatasetPlaceholder(),
        preprocessors.span_corruption,
        seqio.preprocessors.append_eos_after_trim,
    ],
    output_features=DEFAULT_OUTPUT_FEATURES,
    metric_fns=[])

TaskRegistry.add(
    "iskonawa_iid_denoising",
    source=seqio.TextLineDataSource(split_to_filepattern=datasplit),
    preprocessors=[
        functools.partial(
            preprocessors.parse_tsv),
        seqio.preprocessors.tokenize,
        #seqio.CacheDatasetPlaceholder(),
        preprocessors.iid_denoising,
        seqio.preprocessors.append_eos_after_trim,
    ],
    output_features=DEFAULT_OUTPUT_FEATURES,
    metric_fns=[])

MixtureRegistry.add(
    "mixture_iskonawa_test",
    ["iskonawa_span_corruption", "iskonawa_iid_denoising"],
    default_rate=1.0
    )
