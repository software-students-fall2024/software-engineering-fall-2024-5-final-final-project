from flask import Blueprint, request, send_file
from pylatex import Document, Section, Subsection, Command, Itemize
from pylatex.utils import NoEscape
import os

TEMP_LATEX_FILE = 'temp'
TEMP_PDF_FILE = 'temp.pdf'

# Create a Blueprint instance
resume_bp = Blueprint('resume', __name__)

@resume_bp.route('/generate_resume', methods=['POST'])
def generate_resume():
    # get form data
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    linkedin = request.form['linkedin']
    github = request.form['github']

    # education info
    education_data = []
    i = 1
    while f'institution{i}' in request.form:
        education_data.append({
            'institution': request.form[f'institution{i}'],
            'degree': request.form[f'degree{i}'],
            'location': request.form[f'location{i}'],
            'date': request.form[f'date{i}']
        })
        i += 1

    # experience info
    experience_data = []
    i = 1
    while f'company{i}' in request.form:
        experience_data.append({
            'company': request.form[f'company{i}'],
            'role': request.form[f'role{i}'],
            'location': request.form[f'location{i}'],
            'date': request.form[f'date{i}'],
            'responsibilities': request.form[f'responsibilities{i}']
        })
        i += 1

    # projects info
    project_data = []
    i = 1
    while f'projectName{i}' in request.form:
        project_data.append({
            'name': request.form[f'projectName{i}'],
            'tech': request.form[f'projectTech{i}'],
            'date': request.form[f'projectDate{i}'],
            'details': request.form[f'projectDetails{i}']
        })
        i += 1

    # technical info
    languages = request.form['languages']
    frameworks = request.form['frameworks']
    tools = request.form['tools']
    libraries = request.form['libraries']

    # create latex doc
    doc = Document()
    doc.preamble.append(Command('title', 'Resume'))
    doc.preamble.append(Command('author', name))
    doc.append(NoEscape(r'\maketitle'))

    # set up latex packages
    doc.preamble.append(NoEscape(r'''
\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\input{glyphtounicode}

% Custom fonts and page layout
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.5in}
\addtolength{\textheight}{1.0in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

\titleformat{\section}{\vspace{-4pt}\scshape\raggedright\large}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubSubheading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \textit{\small#1} & \textit{\small #2} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & #2 \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}
'''))

    # personal info
    with doc.create(Section('Personal Information')):
        doc.append(f"Phone: {phone}\n")
        doc.append(f"Email: {email}\n")
        if linkedin:
            doc.append(f"LinkedIn: {linkedin}\n")
        if github:
            doc.append(f"GitHub: {github}\n")

    # education section
    with doc.create(Section('Education')):
        for edu in education_data:
            with doc.create(Subsection(edu['institution'])):
                doc.append(f"Degree: {edu['degree']}\n")
                doc.append(f"Location: {edu['location']}\n")
                doc.append(f"Date: {edu['date']}\n")

    # experience section
    with doc.create(Section('Experience')):
        for exp in experience_data:
            with doc.create(Subsection(exp['company'])):
                doc.append(f"Role: {exp['role']}\n")
                doc.append(f"Location: {exp['location']}\n")
                doc.append(f"Date: {exp['date']}\n")
                doc.append("Responsibilities:\n")
                with doc.create(Itemize()) as itemize:
                    itemize.add_item(exp['responsibilities'])

    # projects section
    with doc.create(Section('Projects')):
        for project in project_data:
            with doc.create(Subsection(project['name'])):
                doc.append(f"Technologies Used: {project['tech']}\n")
                doc.append(f"Date: {project['date']}\n")
                doc.append(f"Details: {project['details']}\n")

    # technical skills section
    with doc.create(Section('Technical Skills')):
        doc.append(f"Languages: {languages}\n")
        doc.append(f"Frameworks: {frameworks}\n")
        doc.append(f"Developer Tools: {tools}\n")
        doc.append(f"Libraries: {libraries}\n")

    # save the LaTeX file as "temp.tex"
    doc.generate_tex(TEMP_LATEX_FILE)

    # compile LaTeX to PDF (overwrite temp.pdf)
    os.system(f"pdflatex {TEMP_LATEX_FILE}")

    # provide the generated PDF to the user
    return send_file(TEMP_PDF_FILE, as_attachment=True)