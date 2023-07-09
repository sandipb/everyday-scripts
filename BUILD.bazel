load("//:my_custom.bzl", "write_new_file")
load("@rules_python//python:defs.bzl", "py_binary")

py_binary(
    name = "photo_label",
    srcs = ["photo_label.py"],
)

write_new_file(
    name = "write_my_cstom_msg_to_file",
    input_file = "//:input.txt",
    output_file = "awesome_output",
)

write_new_file(
    name = "write_again",
    input_file = "//:input.txt",
    output_file = "awesome_output_again",
)
