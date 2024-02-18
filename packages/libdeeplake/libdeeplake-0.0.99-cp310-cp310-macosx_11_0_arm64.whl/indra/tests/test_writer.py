from indra import api
import numpy as np
import pytest
import deeplake
from .utils import tmp_datasets_dir, data_path


def test_empty_shape_data_append(tmp_datasets_dir):
    dw = api.dataset_writer(str(tmp_datasets_dir / "empty_shape/"))

    dw.create_tensor("labels", htype="class_label")

    with dw:
        dw.labels.extend(np.uint32(1))
        dw.labels.extend(np.uint32(11))
        dw.labels.extend(np.uint32(111))
        dw.labels.extend(np.uint32(1111))

    ds = deeplake.load(tmp_datasets_dir / "empty_shape")

    assert len(ds) == 4
    assert ds.labels[0].numpy() == np.uint32(1)
    assert ds.labels[1].numpy() == np.uint32(11)
    assert ds.labels[2].numpy() == np.uint32(111)
    assert ds.labels[3].numpy() == np.uint32(1111)


def test_string_data_append(tmp_datasets_dir):
    dw = api.dataset_writer(str(tmp_datasets_dir / "string_dataset/"))

    print(str(tmp_datasets_dir / "string_dataset/"))
    dw.create_tensor("sentences", htype="text")

    sentences = [
        "This is a sentence.",
        "This is another sentence.",
        "This is a third sentence.",
        "This is a fourth sentence.",
    ]

    with dw:
        dw.sentences.extend(sentences)
        dw.sentences.extend("This is a fifth sentence.")
        sentences.append("This is a fifth sentence.")

    ds = deeplake.load(tmp_datasets_dir / "string_dataset")

    assert len(ds) == 5
    assert ds.sentences[0].tobytes() == sentences[0].encode("utf-8")
    assert ds.sentences[1].tobytes() == sentences[1].encode("utf-8")
    assert ds.sentences[2].tobytes() == sentences[2].encode("utf-8")
    assert ds.sentences[3].tobytes() == sentences[3].encode("utf-8")
    assert ds.sentences[4].tobytes() == sentences[4].encode("utf-8")
