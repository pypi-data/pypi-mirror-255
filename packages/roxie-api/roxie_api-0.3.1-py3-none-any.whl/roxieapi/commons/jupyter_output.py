from IPython.display import HTML, display


def display_3d_output(file: str) -> None:
    """Display 3d File within Jupyter

     Uses X_ITE X3D Browser to visualize 3d files.

    Parameters:
    file: str The file to show (VRML, X3D)
    """

    html_str = """<html>
    <head>
        <meta charset="utf-8"/>
        <link rel="stylesheet" type="text/css" href="https://create3000.github.io/code/x_ite/latest/dist/x_ite.css"/>
        <script type="text/javascript" src="https://create3000.github.io/code/x_ite/latest/dist/x_ite.min.js"></script>
        <style type="text/css">
    X3DCanvas {{
    width: 768px;
    height: 432px;
    }}
        </style>
    </head>
    <body>
        <X3DCanvas src="{0}">
        <p>Your browser may not support all features required by X_ITE.
            For a better experience, keep your browser up to date.
            <a href="http://outdatedbrowser.com">Check here for latest versions.</a></p>
        </X3DCanvas>
    </body>
    </html>
    """.format(
        file
    )

    display(HTML(html_str))
