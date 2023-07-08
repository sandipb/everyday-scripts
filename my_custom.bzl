def write_new_file_impl(ctx):
    output_file = ctx.actions.declare_file(ctx.attr.output_file + ".txt")
    ctx.actions.run(
        outputs = [output_file],
        inputs = [ctx.file.input_file],
        executable = "cp",
        arguments = [ctx.file.input_file.path, output_file.path],
    )
    return DefaultInfo(files = depset([output_file]))

write_new_file = rule(
    implementation = write_new_file_impl,
    attrs = {
        "input_file": attr.label(allow_single_file = True),
        "output_file": attr.string(),
    },
)
