import os
from pathlib import Path

from more_than_inference.utils.register import META


def build_proto(dist_dir, proto_dir):  # install mypy-protobuf first
    os.system(f'protoc --python_out={dist_dir} --mypy_out={dist_dir} --proto_path={dist_dir} {proto_dir}/*.proto')


def clean_proto(proto_dir):
    os.system(f'rm -fr {proto_dir}/*_pb2.py')


@META.regist_cmd()
def refresh_proto(args):
    dist_root = Path(__file__).resolve().parent.parent
    dist_dir = dist_root.parent
    proto_dir = dist_root / "protos"
    clean_proto(proto_dir)
    build_proto(dist_dir, proto_dir)
