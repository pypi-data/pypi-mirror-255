# (c) 2015-2023 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
import re


class _Tests:
    def __init__(self, config, cls) -> None:
        if cls.files is None:
            return

        for key in config:
            attr_name = key

            # Ensure attribute name starts with a letter
            if not attr_name[0].isalpha():
                attr_name = f"test_{attr_name}"

            # Replace non-alphanumeric (and _) characters with _
            attr_name = re.sub(r"[^a-zA-Z0-9_]", "_", attr_name)

            try:
                setattr(self, attr_name, _Test(attr_name, config[key], cls))
            except Exception:
                import traceback

                print(
                    f"Failed to set-up test {key} for app {cls} with traceback: {traceback.format_exc()}"
                )

    def __str__(self) -> str:
        descr = ""
        for key in self.__dict__:
            descr += f"{self.__dict__[key]}\n"
        return descr

    def __repr__(self) -> str:
        return self.__str__()


class _Test:
    def __init__(self, name, config, cls) -> None:
        args = config["arguments"].copy()
        for key, vals in args.items():
            if not isinstance(vals, (list, tuple)):
                vals = [vals]

            for i in range(len(vals)):
                val = vals[i]
                if not isinstance(val, str):
                    continue
                if val.startswith("tests/"):
                    if val.endswith("/"):
                        val = val[:-1]
                    vals[i] = cls.files[val]
                if val.startswith("datasets/"):
                    vals[i] = getattr(cls.datasets, val.replace("datasets/", ""))
                if val.startswith("artifacts/"):
                    if not hasattr(cls, "artifacts"):
                        raise RuntimeError(
                            f"Test {name} of app '{cls._name}' requires file {val} but the app manifest is missing the artifacts section"
                        )
                    vals[i] = getattr(cls.artifacts, val.replace("artifacts/", ""))
            args[key] = vals if len(vals) > 1 else vals[0]
        config["arguments"] = args

        self.name = name
        self.config = config
        self.cls = cls

    def run(self, queue=None, **kwargs):
        from playmolecule import PM_APP_ROOT, JobStatus
        import tempfile
        import time
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            print(
                f"Running test '{self.name}' at location {tmpdir} with args {self.config['arguments']}"
            )

            t = time.time()
            ed = self.cls.__call__(outdir=tmpdir, **self.config["arguments"])
            ed.run(queue=queue, **kwargs)

            if PM_APP_ROOT.startswith("http"):
                while ed.status not in (JobStatus.COMPLETED, JobStatus.ERROR):
                    time.sleep(10)

            for ff in self.config["expected_outputs"]:
                if not os.path.exists(os.path.join(tmpdir, ff)):
                    raise RuntimeError(
                        f"Test failed. Could not find expected output file: {ff} in {tmpdir}"
                    )
            print(f"\n🎉 Test '{self.name}' succeeded in {time.time()-t:.2f} seconds! 🎉")

    def __str__(self) -> str:
        descr = self.config["description"]
        string = f"[{self.name}] '{descr}'\n- Arguments:\n"
        for arg, val in self.config["arguments"].items():
            string += f"  {arg} = {val}\n"
        string += "- Expected outputs:\n"
        for outp in self.config["expected_outputs"]:
            string += f"  {outp}\n"
        return string

    def __repr__(self) -> str:
        return self.__str__()
