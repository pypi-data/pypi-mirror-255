import subprocess


def convert_tex_to_pdf(tex_file):
    try:
        subprocess.run(['pdflatex', tex_file])
        print("PDF successfully generated!")
    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    tex_file = './test.tex'
    convert_tex_to_pdf(tex_file)
