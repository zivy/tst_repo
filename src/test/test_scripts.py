import pytest
import pathlib
import hashlib
from validate_data import validate_data
from csv_roadmap_2_md_url import csv_2_md_with_url
from csv_2_supporting import csv_2_supporting
from csv_multi_2_csv_single import csv_multi_2_csv_single
from bib2md import bibfile2md


class BaseTest:
    def setup_method(self):
        # Path to testing data is expected in the following location:
        self.data_path = pathlib.Path(__file__).parent.absolute() / "data"

    def files_md5(self, file_path_list):
        """
        Compute a single/combined md5 hash for a list of files.
        """
        md5 = hashlib.md5()
        for file_name in file_path_list:
            with open(file_name, "rb") as fp:
                for mem_block in iter(lambda: fp.read(128 * md5.block_size), b""):
                    md5.update(mem_block)
        return md5.hexdigest()


class TestValidation(BaseTest):
    @pytest.mark.parametrize(
        "json_config_file, roadmap_csv, supporting_material_root_dir, zenodo_json, result",
        [
            (
                "validate_data_config.json",
                "roadmap.csv",
                "supporting_material",
                "zenodo.json",
                0,
            ),
            (
                "validate_data_config.json",
                "contradictory_endorsement.csv",
                "supporting_material",
                "zenodo.json",
                1,
            ),
            (
                "validate_data_config.json",
                "missing_required_data.csv",
                "supporting_material",
                "zenodo.json",
                1,
            ),
            (
                "validate_data_config.json",
                "orcid_not_in_zenodo.csv",
                "supporting_material",
                "zenodo.json",
                1,
            ),
            (
                "validate_data_config.json",
                "repeated_column_entry.csv",
                "supporting_material",
                "zenodo.json",
                1,
            ),
            (
                "validate_data_config.json",
                "repeated_target_conjugate_row.csv",
                "supporting_material",
                "zenodo.json",
                1,
            ),
            (
                "validate_data_config.json",
                "unexpected_value.csv",
                "supporting_material",
                "zenodo.json",
                1,
            ),
        ],
    )
    def test_validate_data(
        self,
        json_config_file,
        roadmap_csv,
        supporting_material_root_dir,
        zenodo_json,
        result,
    ):
        res = validate_data(
            json_config_file,
            self.data_path / roadmap_csv,
            self.data_path / supporting_material_root_dir,
            self.data_path / zenodo_json,
        )
        assert res == result


class TestCSV2MD(BaseTest):
    @pytest.mark.parametrize(
        "csv_file_name, supporting_material_root_dir, result_md5hash",
        [("roadmap.csv", "supporting_material", "1c640aeba06dc5a58790396fdbf5aa54")],
    )
    def test_csv_2_md_with_url(
        self, csv_file_name, supporting_material_root_dir, result_md5hash
    ):
        csv_2_md_with_url(
            self.data_path / csv_file_name,
            self.data_path / supporting_material_root_dir,
        )
        assert (
            self.files_md5([(self.data_path / csv_file_name).with_suffix(".md")])
            == result_md5hash
        )


class TestCSV2Supporting(BaseTest):
    @pytest.mark.parametrize(
        "csv_file_name, supporting_template_file, shared_reasoning_file, result_md5hash",
        [
            (
                "batch_supporting.csv",
                "supporting_template.md",
                "shared_reasoning.md",
                "eb0b405c9a94800d9bb159ca41aed349",
            )
        ],
    )
    def test_csv_2_supporting(
        self,
        csv_file_name,
        supporting_template_file,
        shared_reasoning_file,
        result_md5hash,
        tmp_path,
    ):
        # Write the output using the tmp_path fixture
        file_names = csv_2_supporting(
            self.data_path / csv_file_name,
            tmp_path,
            self.data_path / supporting_template_file,
            self.data_path / shared_reasoning_file,
        )
        assert self.files_md5(file_names) == result_md5hash


class TestCSVMulti2CSVSingle(BaseTest):
    @pytest.mark.parametrize(
        "csv_multi_file_name, result_md5hash",
        [
            (
                "roadmap_multi.csv",
                "328f5ed75e7388265371be0cc5bc9e9b",
            )
        ],
    )
    def test_csv_multi_2_csv_single(
        self,
        csv_multi_file_name,
        result_md5hash,
        tmp_path,
    ):
        single_df = csv_multi_2_csv_single(self.data_path / csv_multi_file_name)
        # Write the output using the tmp_path fixture
        output_file_path = tmp_path / "roadmap_single.csv"
        single_df.to_csv(output_file_path, index=False)
        assert self.files_md5([output_file_path]) == result_md5hash


class TestBib2MD(BaseTest):
    @pytest.mark.parametrize(
        "bib_file_name, csl_file_name, result_md5hash",
        [("publications.bib", "ieee.csl", "3aac161fb3698fc72ece5e9dbe799c7c")],
    )
    def test_bib_2_md(self, bib_file_name, csl_file_name, result_md5hash, tmp_path):
        # Write the output using the tmp_path fixture
        output_file_path = tmp_path / "publications.md"
        bibfile2md(
            self.data_path / bib_file_name,
            self.data_path / csl_file_name,
            output_file_path,
        )
        assert self.files_md5([output_file_path]) == result_md5hash
