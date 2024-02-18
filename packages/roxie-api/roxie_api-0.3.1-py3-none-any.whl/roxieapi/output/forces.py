def update_force2d_with_field_scaling(
    roxie_force_input_path: str,
    roxie_force_output_path: str,
    field: float,
    target_field: float,
) -> None:
    """Static method scaling ROXIE force with actual and target field

    :param roxie_force_input_path: input path with ROXIE Lorentz force
    :param roxie_force_output_path: output path with ROXIE Lorentz force
    :param field: actual field in tesla
    :param target_field: target field in tesla
    """
    with open(roxie_force_input_path, "r") as f:
        roxie_force_txt = f.readlines()

    # # convert text input to a list of floats
    scaling = (target_field / field) ** 2
    roxie_force = []
    for roxie_force_txt_el in roxie_force_txt:
        row_float = [
            float(el)
            for el in roxie_force_txt_el.replace("\n", "").split(" ")
            if el != ""
        ]
        row_float[2] *= scaling
        row_float[3] *= scaling
        roxie_force.append(row_float)

    with open(roxie_force_output_path, "w") as file_write:
        for roxie_force_el in roxie_force:
            row_str = [str(roxie_force_el_el) for roxie_force_el_el in roxie_force_el]
            file_write.write(" ".join(row_str) + "\n")


def convert_roxie_force_file_to_ansys(
    input_force_file_path: str, output_force_file_path: str
) -> None:
    """Function preparing a force file for ANSYS from a ROXIE Lorentz force file, .force2d

    :param input_force_file_path: a name of a ROXIE Lorentz force file
    :param output_force_file_path: a name of an output file for ANSYS
    """
    with open(input_force_file_path, "r") as f:
        force_txt = f.readlines()

    ansys_force = []
    for force_txt_el in force_txt:
        row_float = [
            float(el) for el in force_txt_el.replace("\n", "").split(" ") if el != ""
        ]
        ansys_force.append("nodeNum = NODE(%f, %f, 0.0)" % tuple(row_float[:2]))
        ansys_force.append("F,nodeNum,FX, %f" % row_float[2])
        ansys_force.append("F,nodeNum,FY, %f" % row_float[3])

    with open(output_force_file_path, "w") as f:
        f.writelines(ansys_force)
