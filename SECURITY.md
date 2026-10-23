# Input trust

RenderCV is a local document generator. Render CV files and custom themes that
you trust. Input files can reference local files and remote photo URLs, contain
Typst expressions, and select custom themes that include Python code.

Absolute paths and paths outside the input directory are supported deliberately,
for example when several CVs share a photo or a theme. Photo validation rejects
files that do not have a supported image signature; it does not enforce filesystem
containment or make an image safe to disclose.

Services that accept untrusted CVs must isolate each render from host secrets and
other users' files, restrict network access, and control which themes and files
are available to the renderer. Validating the YAML schema is not a substitute for
that isolation.

To report a security problem privately, contact dev@atalay.biz with a reproducer
and the affected RenderCV version.
