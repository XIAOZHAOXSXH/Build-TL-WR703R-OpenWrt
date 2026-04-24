import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "collect_release_ipks.py"


class CollectReleaseIpksTest(unittest.TestCase):
    def test_malformed_packages_line_does_not_abort_collection(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            bin_packages = temp_path / "bin" / "packages"
            output_dir = temp_path / "release"
            package_dir = bin_packages / "custom"
            package_dir.mkdir(parents=True)

            packages_file = package_dir / "Packages"
            packages_file.write_text(
                "\n".join(
                    [
                        "Package: luci-light",
                        "Version: 1",
                        "Depends: +rpcd",
                        "Filename: custom/luci-light_1_all.ipk",
                        "Description: LuCI meta package",
                        "This line is malformed but should not break parsing",
                        "",
                        "Package: rpcd",
                        "Version: 1",
                        "Filename: custom/rpcd_1_mips_24kc.ipk",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            for filename in ("luci-light_1_all.ipk", "rpcd_1_mips_24kc.ipk"):
                (package_dir / filename).write_text("dummy", encoding="utf-8")

            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--bin-packages",
                    str(bin_packages),
                    "--output",
                    str(output_dir),
                    "--seed",
                    "luci-light",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output_dir / "luci-light_1_all.ipk").exists())
            self.assertTrue((output_dir / "rpcd_1_mips_24kc.ipk").exists())
            self.assertEqual(
                (output_dir / "package-manifest.txt").read_text(encoding="utf-8"),
                "luci-light\tluci-light_1_all.ipk\nrpcd\trpcd_1_mips_24kc.ipk\n",
            )


if __name__ == "__main__":
    unittest.main()
