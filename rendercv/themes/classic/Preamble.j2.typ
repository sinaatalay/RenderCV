%% start of file `template.tex'.
%% Copyright 2006-2015 Xavier Danaux (xdanaux@gmail.com), 2020-2022 moderncv maintainers (github.com/moderncv).
%
% This work may be distributed and/or modified under the
% conditions of the LaTeX Project Public License version 1.3c,
% available at http://www.latex-project.org/lppl/.

\documentclass[<<design.font_size>>,<<design.page_size>>,sans]{moderncv}        % possible options include font size ('10pt', '11pt' and '12pt'), paper size ('a4paper', 'letterpaper', 'a5paper', 'legalpaper', 'executivepaper' and 'landscape') and font family ('sans' and 'roman')

% moderncv themes
\moderncvstyle{classic}                            % style options are 'casual' (default), 'classic', 'banking', 'oldstyle' and 'fancy'
\moderncvcolor{<<design.color>>}                               % color options 'black', 'blue' (default), 'burgundy', 'green', 'grey', 'orange', 'purple' and 'red'
%\renewcommand{\familydefault}{\sfdefault}         % to set the default font; use '\sfdefault' for the default sans serif font, '\rmdefault' for the default roman one, or any tex font name
((* if design.disable_page_numbers *))
\nopagenumbers{}
((* endif *))

\usepackage{amsmath} % for math

% adjust the page margins
\usepackage[scale=<<design.content_scale>>]{geometry}
\setlength{\hintscolumnwidth}{<<design.date_width>>}                % if you want to change the width of the column with the dates
%\setlength{\makecvheadnamewidth}{10cm}            % for the 'classic' style, if you want to force the width allocated to your name and avoid line breaks. be careful though, the length is normally calculated to avoid any overlap with your personal info; use this at your own typographical risks...

% font loading
% for luatex and xetex, do not use inputenc and fontenc
% see https://tex.stackexchange.com/a/496643
\ifxetexorluatex
  \usepackage{fontspec}
  \usepackage{unicode-math}
  \defaultfontfeatures{Ligatures=TeX}
  \setmainfont{Latin Modern Roman}
  \setsansfont{Latin Modern Sans}
  \setmonofont{Latin Modern Mono}
  \setmathfont{Latin Modern Math} 
\else
  \usepackage[T1]{fontenc}
  \usepackage{lmodern}
\fi

% document language
\usepackage[english]{babel}  % FIXME: using spanish breaks moderncv

% personal data
\name{<<cv.name>>}{}
((* if cv.label *))
\title{<<cv.label>>}                               % optional, remove / comment the line if not wanted
((* endif *))
% \familyname{}
((* if cv.location *))
\address{<<cv.location>>}{}
((* endif *))
((* if cv.phone *))
\phone[mobile]{<<cv.phone|replace("tel:", "")|replace("-"," ")>>}
((* endif *))
((* if cv.email *))
\email{<<cv.email|escape_latex_characters>>}
((* endif *))
((* if cv.website *))
\homepage{<<cv.website|replace("https://", "")|reverse|replace("/", "", 1)|reverse>>}
((* endif *))

((* if cv.social_networks *))
    ((* for network in cv.social_networks *))
\social[<<network.network|lower()|replace(" ", "")>>]{<<network.username>>}
    ((* endfor *))
((* endif *))
% Social icons
% \social[linkedin]{john.doe}                        % optional, remove / comment the line if not wanted
% \social[xing]{john\_doe}                           % optional, remove / comment the line if not wanted
% \social[twitter]{ji\_doe}                          % optional, remove / comment the line if not wanted
% \social[github]{jdoe}                              % optional, remove / comment the line if not wanted
% \social[gitlab]{jdoe}                              % optional, remove / comment the line if not wanted
% \social[stackoverflow]{0000000/johndoe}            % optional, remove / comment the line if not wanted
% \social[bitbucket]{jdoe}                           % optional, remove / comment the line if not wanted
% \social[skype]{jdoe}                               % optional, remove / comment the line if not wanted
% \social[orcid]{0000-0000-000-000}                  % optional, remove / comment the line if not wanted
% \social[researchgate]{jdoe}                        % optional, remove / comment the line if not wanted
% \social[researcherid]{jdoe}                        % optional, remove / comment the line if not wanted
% \social[telegram]{jdoe}                            % optional, remove / comment the line if not wanted
% \social[whatsapp]{12345678901}                     % optional, remove / comment the line if not wanted
% \social[signal]{12345678901}                       % optional, remove / comment the line if not wanted
% \social[matrix]{@johndoe:matrix.org}               % optional, remove / comment the line if not wanted
% \social[googlescholar]{googlescholarid}            % optional, remove / comment the line if not wanted

% new command for cventry (this is done to allow users unbold or unitalicize the text in the cventry command)
\renewcommand*{\cventry}[6][.25em]{%
  \cvitem[#1]{#2}{%
    #3%
    \ifthenelse{\equal{#4}{}}{}{, #4}%
    \ifthenelse{\equal{#5}{}}{}{, #5}%
    \ifthenelse{\equal{#6}{}}{}{, #6}%
  }
}

((* if cv.photo *))
\photo[3cm][1pt]{<<cv.photo.name>>}
((* endif *))