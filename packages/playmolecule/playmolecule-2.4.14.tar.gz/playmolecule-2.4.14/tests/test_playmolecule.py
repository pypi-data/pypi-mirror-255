from distutils import dir_util
from pytest import fixture
import os


@fixture
def datadir(tmpdir, request):
    """
    Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.
    """
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)

    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmpdir))

    return tmpdir


def prepare(datadir):
    outdir = str(datadir.join("out"))
    scratchdir = str(datadir.join("scratch"))
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(scratchdir, exist_ok=True)
    return outdir, scratchdir


def _test_playmolecule(datadir):
    datadir = str(datadir)
    os.environ["PM_APP_ROOT"] = datadir

    from playmolecule import apps, datasets, protocols
    import tempfile

    assert hasattr(apps, "proteinprepare")
    assert hasattr(apps.proteinprepare, "tests")
    assert hasattr(apps.proteinprepare, "files")
    assert hasattr(apps.proteinprepare.v1, "tests")
    assert hasattr(apps.proteinprepare.v1, "files")
    assert hasattr(apps.proteinprepare.v1.tests, "simple")
    assert sorted(list(apps.proteinprepare.v1.files.keys())) == sorted(
        [
            "datasets",
            "datasets/3ptb.pdb",
            "tests",
            "tests/web_content.pickle",
            "tests/reprepare.pickle",
            "tests/3ptb.pdb",
            "tests/587HG92V.pdb",
            "tutorials",
            "tutorials/learn_this_app.ipynb",
        ]
    )
    assert hasattr(apps.proteinprepare.v1.datasets, "file_3ptb")
    assert hasattr(datasets, "file_3ptb")
    assert hasattr(protocols, "crypticscout")
    assert hasattr(protocols.crypticscout, "v1")
    assert hasattr(protocols.crypticscout.v1, "crypticscout")
    assert hasattr(protocols.crypticscout.v1.crypticscout, "crypticscout")
    assert callable(protocols.crypticscout.v1.crypticscout.crypticscout)

    expected_files = [
        ".pm.done",
        ".manifest.json",
        "run.sh",
        "expected_outputs.json",
        "inputs",
        os.path.join("inputs", "inputs.json"),
        os.path.join("inputs", "original_paths.json"),
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        apps.proteinprepare(tmpdir, pdbfile=datasets.file_3ptb).run()
        for ef in expected_files:
            assert os.path.exists(os.path.join(tmpdir, ef))

    expected_files += [os.path.join("inputs", "3ptb.pdb")]
    with tempfile.TemporaryDirectory() as tmpdir:
        apps.proteinprepare(
            tmpdir, pdbfile=os.path.join(datadir, "datasets", "3ptb.pdb")
        ).run()
        for ef in expected_files:
            assert os.path.exists(os.path.join(tmpdir, ef))
