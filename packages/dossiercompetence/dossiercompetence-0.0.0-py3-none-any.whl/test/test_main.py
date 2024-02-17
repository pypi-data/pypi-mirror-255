import pytest
from dossier_competence.main import (
    trigrammer,
    file_name_anonimized,
    file_name,
    get_trigrammer,
    get_file_name,
    get_output_name,
    TrigrammerError,
)


# part test


def test_trigrammer():
    print("____test_trigrammer____")
    assert trigrammer("yao.xin") == "xya"
    assert trigrammer("yyy.xin") == "xyy"
    assert trigrammer("y_dsqghjao.xin") == "xy_"
    assert trigrammer("yqsdg_dsqghjao.xin") == "xyq"
    assert trigrammer("yao.jin.xin") == "jya"  # Identifiez le premier point


def test_trigrammer_failed():
    with pytest.raises(TrigrammerError):
        trigrammer("yao..xin")


def test_file_name_anonimized():
    print("____test_file_name_anonimized____")
    assert file_name_anonimized("dataScience.md") == "dataScience_a"
    assert file_name_anonimized("data_science.md") == "data_science_a"
    assert file_name_anonimized("data.science.md") == "data.science_a"
    assert file_name_anonimized("datascience") == "datascience_a"
    assert file_name_anonimized("data.science.txt") == "data.science.txt_a"


def test_file_name():
    print("____test_file_name____")
    assert file_name("dataScience.md") == "dataScience"
    assert file_name("data_science.md") == "data_science"
    assert file_name("data.science.md") == "data.science"
    assert file_name("data.md_science.md") == "data"
    assert file_name("data") == "data"


def test_get_trigrammer():
    print("____test_get_trigrammer____")
    assert get_trigrammer("yao.xin/dataScience.md") == "yao.xin"
    assert get_trigrammer("yaoxin/dataScience.md") == "yaoxin"
    assert get_trigrammer("yao/xin/dataScience.md") == "xin"
    assert get_trigrammer("y/a/o/xin/dataScience.md") == "xin"
    assert get_trigrammer("y//a//o/xin/dataScience.md") == "xin"
    assert get_trigrammer("y//a//o//xin//dataScience.md") == ""


def test_get_trigrammer_failed():
    with pytest.raises(TrigrammerError):
        get_trigrammer("xin.dataScience.md")


def test_get_file_name():
    print("____test_get_file_name____")
    assert get_file_name("yao.xin/dataScience.md") == "dataScience.md"
    assert get_file_name("yao/xin/dataScience.md") == "dataScience.md"
    assert get_file_name("y/a/o/xin/dataScience.md") == "dataScience.md"
    assert get_file_name("xin.dataScience.md") == "xin.dataScience.md"


def test_get_output_name():
    print("____test_get_output_name____")
    assert (
        get_output_name("yao.xin/dataScience.md", anonimized=True)
        == "xya/dataScience_a"
    )
    assert (
        get_output_name("yao/abc.xin/dataScience.md", anonimized=True)
        == "xab/dataScience_a"
    )
    assert (
        get_output_name("y/a/o/ab.x/dataScience.md", anonimized=True)
        == "xab/dataScience_a"
    )
    assert (
        get_output_name("yao.xin/dataScience.md", anonimized=False)
        == "xya/dataScience"
    )
    assert (
        get_output_name("yao/abc.xin/dataScience.md", anonimized=False)
        == "xab/dataScience"
    )
    assert (
        get_output_name("y/a/o/ab.x/dataScience.md", anonimized=False)
        == "xab/dataScience"
    )


if __name__ == "__main__":
    pytest.main(["-s", "test_main.py"])
