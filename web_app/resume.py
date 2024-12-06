from flask import Blueprint, request, send_file
from pylatex import Document, Section, Subsection, Command, Itemize
from pylatex.utils import NoEscape
import os

TEMP_LATEX_FILE = 'temp'
TEMP_PDF_FILE = 'temp.pdf'

# create blueprint instance
resume_bp = Blueprint('resume', __name__)

@resume_bp.route('/generate_resume', methods=['POST'])
def generate_resume():
    # get form data
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    linkedin = request.form.get('linkedin', '')
    github = request.form.get('github', '')

    # education info
    education_data = []
    i = 1
    while f'institution{i}' in request.form:
        education_data.append({
            'institution': request.form[f'institution{i}'],
            'degree': request.form[f'degree{i}'],
            'date': request.form[f'date{i}'],
            'location': request.form[f'location{i}']
        })
        i += 1

    # experience info
    experience_data = []
    i = 1
    while f'company{i}' in request.form:
        experience_data.append({
            'company': request.form[f'company{i}'],
            'role': request.form[f'role{i}'],
            'location': request.form[f'expLocation{i}'],
            'date': request.form[f'expDate{i}'],
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
    languages = request.form.get('languages')
    frameworks = request.form.get('frameworks')
    tools = request.form.get('tools')
    libraries = request.form.get('libraries')

    # create latex doc
    doc = Document()

    # set up latex packages
    doc.preamble.append(NoEscape(r'''
        \usepackage{latexsym}
        \usepackage[empty]{fullpage}
        \usepackage{titlesec}
        \usepackage{marvosym}
        \usepackage[usenames,dvipsnames]{color}
        \usepackage{verbatim}
        \usepackage{enumitem}
        \usepackage[hidelinks]{hyperref}
        \usepackage{fancyhdr}
        \usepackage[english]{babel}
        \usepackage{tabularx}
        \input{glyphtounicode}

        \pagestyle{fancy}
        \fancyhf{} % clear all header and footer fields
        \fancyfoot{}
        \renewcommand{\headrulewidth}{0pt}
        \renewcommand{\footrulewidth}{0pt}

        % adjust margins
        \addtolength{\oddsidemargin}{-0.5in}
        \addtolength{\evensidemargin}{-0.5in}
        \addtolength{\textwidth}{1in}
        \addtolength{\topmargin}{-.5in}
        \addtolength{\textheight}{1.0in}

        \urlstyle{same}

        \raggedbottom
        \raggedright
        \setlength{\tabcolsep}{0in}

        \titleformat{\section}{
            \vspace{-4pt}\scshape\raggedright\large
        }{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

        \pdfgentounicode=1
                                 
        \newcommand{\resumeItem}[1]{
            \item\small{
                {#1 \vspace{-2pt} }
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
        \newcommand{\resumeItemListStart}{\begin{itemize}[label=\textbullet]}
        \newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}
        '''))

    # add header
    doc.preamble.append(NoEscape(r'''
        \usepackage{hyperref}
        \usepackage{geometry}
        \geometry{top=1in, bottom=1in, left=1in, right=1in}
        \usepackage{enumitem}

        \pagestyle{empty}

        % Custom header command
        \newcommand{\customheader}[5]{%
            \begin{center}
                \textbf{\Huge \scshape #1} \\ \vspace{1pt}
                \small #2 $|$ \href{mailto:#3}{\underline{#3}} $|$
                \href{https://linkedin.com/in/#4}{\underline{linkedin.com/in/#4}} $|$
                \href{https://github.com/#5}{\underline{github.com/#5}}
            \end{center}
        }
    '''))

    doc.append(NoEscape(r'\customheader{%s}{%s}{%s}{%s}{%s}' % (
        name, 
        phone if phone else '', 
        email if email else '', 
        linkedin if linkedin else '', 
        github if github else ''
    )))

    # education section
    if education_data:
        doc.append(NoEscape(r'\section{Education}'))
        doc.append(NoEscape(r'\resumeSubHeadingListStart'))  # Start the list
        for edu in education_data:
            doc.append(NoEscape(r'\resumeSubheading{%s}{%s}{%s}{%s}' % (
                edu['institution'],
                edu['date'],
                edu['degree'],
                edu['location']
            )))
        doc.append(NoEscape(r'\resumeSubHeadingListEnd'))

    # experience section
    if experience_data:
        doc.append(NoEscape(r'\section{Experience}'))
        
        for exp in experience_data:
            doc.append(NoEscape(r'\resumeSubHeadingListStart'))  
            
            doc.append(NoEscape(r'\resumeSubheading{%s}{%s}{%s}{%s}' % (
                exp['role'],
                exp['date'],
                exp['company'],
                exp['location']
            )))
            
            doc.append(NoEscape(r'\resumeItemListStart'))

            responsibilities = exp['responsibilities'].split(';')
            for responsibility in responsibilities:
                if responsibility.strip():
                    doc.append(NoEscape(r'\resumeItem{%s}' % responsibility.strip()))
            
            doc.append(NoEscape(r'\resumeItemListEnd'))
            doc.append(NoEscape(r'\resumeSubHeadingListEnd'))

    # projects section
    if project_data:
        doc.append(NoEscape(r'\section{Projects}'))
        doc.append(NoEscape(r'\resumeSubHeadingListStart'))
        
        for proj in project_data:
            doc.append(NoEscape(r'\resumeProjectHeading{\textbf{%s} $|$ \emph{%s}}{%s}' % (
                proj['name'],
                proj['tech'],
                proj['date']
            )))
            doc.append(NoEscape(r'\resumeItemListStart'))
            details = proj['details'].split(';') 
            for detail in details:
                if detail.strip():
                    doc.append(NoEscape(r'\resumeItem{%s}' % detail.strip()))
            doc.append(NoEscape(r'\resumeItemListEnd'))
        doc.append(NoEscape(r'\resumeSubHeadingListEnd'))

    # tech skillssss
    if languages or frameworks or tools or libraries:
        doc.append(NoEscape(r'\section{Technical Skills}'))
        doc.append(NoEscape(r'\begin{itemize}[leftmargin=0.15in, label={}]'))
        doc.append(NoEscape(r'\small{\item{'))

        # Check if 'languages' is provided and add it
        if languages:
            doc.append(NoEscape(r'\textbf{Languages}{: %s} \\' % languages))
        
        # Check if 'frameworks' is provided and add it
        if frameworks:
            doc.append(NoEscape(r'\textbf{Frameworks}{: %s} \\' % frameworks))
        
        # Check if 'tools' is provided and add it
        if tools:
            doc.append(NoEscape(r'\textbf{Developer Tools}{: %s} \\' % tools))
        
        # Check if 'libraries' is provided and add it
        if libraries:
            doc.append(NoEscape(r'\textbf{Libraries}{: %s} \\' % libraries))
        
        doc.append(NoEscape(r'}}'))
        doc.append(NoEscape(r'\end{itemize}'))

    # save the LaTeX file as "temp.tex"
    doc.generate_tex(TEMP_LATEX_FILE)

    # compile LaTeX to PDF (overwrite temp.pdf)
    os.system(f"pdflatex {TEMP_LATEX_FILE}")

    # provide the generated PDF to the user
    return send_file(TEMP_PDF_FILE, as_attachment=False, mimetype='application/pdf')