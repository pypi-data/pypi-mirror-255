
import tempfile
import os.path as op
from micropype import cached_run, cached_function_call
from micropype.config import Config


def add(x, y, out_f):
    with open(out_f, 'w') as fp:
        fp.write(f"{x+y}")


def test_pipeline():
    tmp_dir = tempfile.TemporaryDirectory()
    
    log_f = op.join(tmp_dir.name, "test.log")
    out_f = op.join(tmp_dir.name, "lsOutput.txt")
    cached_run(
        f"ls -lrt >> {out_f}",
        out_f,
        "Listing current folder items",
        log_f
    )
    with open(out_f, 'r') as fp:
        assert(fp.readline().startswith("total"))

    out_f = op.join(tmp_dir.name, "add.txt")
    cached_function_call(
        add,
        [2, 4.0, out_f],
        [out_f],
        title=f"Addition",
        log=log_f
    )
    with open(out_f, 'r') as fp:
        res = float(fp.readline())
        assert(res == 6)



def test_pipeline_with_config():
    class PipeConfig(Config):
        do_step1: bool = True
        do_step2: bool = True

    cfg = PipeConfig(
        do_step1=True, 
        do_step2=False
    )

    tmp_dir = tempfile.TemporaryDirectory()
    
    log_f = op.join(tmp_dir.name, "test.log")
    out_f = op.join(tmp_dir.name, "lsOutput.txt")
    if cfg.do_step1:
        cached_run(
            f"ls -lrt >> {out_f}",
            out_f,
            "Listing current folder items",
            log_f
        )
    with open(out_f, 'r') as fp:
        assert(fp.readline().startswith("total"))

    out_f = op.join(tmp_dir.name, "add.txt")
    if cfg.do_step2:
        cached_function_call(
            add,
            [2, 4.0, out_f],
            [out_f],
            title=f"Addition",
            log=log_f
        )
    assert(op.isfile(out_f) == False)
