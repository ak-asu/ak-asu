GITHUB_LANG_TO_KEY: dict[str, str] = {
    "Python": "Python",
    "JavaScript": "JavaScript",
    "TypeScript": "TypeScript",
    "Java": "Java",
    "C++": "C++",
    "C#": "C#",
    "Go": "Go",
    "Rust": "Rust",
    "Kotlin": "Kotlin",
    "Swift": "Swift",
    "Ruby": "Ruby",
    "PHP": "PHP",
    "Dart": "Dart",
    "Scala": "Scala",
    "R": "R",
    "Jupyter Notebook": "Jupyter",
    "HTML": "HTML5",
    "CSS": "CSS3",
    "Vue": "Vue.js",
    "C": "C",
}

FILTERED_LANGUAGES: set[str] = {
    "Makefile", "Dockerfile", "YAML", "HCL", "Batchfile", "CMake",
    "Meson", "Nix", "SCSS", "Less", "EJS", "Handlebars", "Smarty",
    "Liquid", "Jinja", "PowerShell", "Vim Script", "EditorConfig",
    "TOML", "INI", "JSON", "XML", "Shell",
}

TECH_BADGE_MAP: dict[str, dict] = {
    # Languages
    "Python":           {"color": "3776AB", "logo": "python"},
    "JavaScript":       {"color": "F7DF1E", "logo": "javascript"},
    "TypeScript":       {"color": "3178C6", "logo": "typescript"},
    "Java":             {"color": "ED8B00", "logo": "openjdk"},
    "C++":              {"label": "C%2B%2B", "color": "00599C", "logo": "cplusplus"},
    "C#":               {"label": "C%23", "color": "239120", "logo": "csharp"},
    "Go":               {"color": "00ADD8", "logo": "go"},
    "Rust":             {"color": "000000", "logo": "rust"},
    "Kotlin":           {"color": "7F52FF", "logo": "kotlin"},
    "Swift":            {"color": "FA7343", "logo": "swift"},
    "Ruby":             {"color": "CC342D", "logo": "ruby"},
    "PHP":              {"color": "777BB4", "logo": "php"},
    "Dart":             {"color": "0175C2", "logo": "dart"},
    "Scala":            {"color": "DC322F", "logo": "scala"},
    "R":                {"color": "276DC3", "logo": "r"},
    "Jupyter":          {"color": "F37626", "logo": "jupyter"},
    "HTML5":            {"color": "E34F26", "logo": "html5"},
    "CSS3":             {"color": "1572B6", "logo": "css3"},
    "Vue.js":           {"color": "35495E", "logo": "vue.js"},
    "C":                {"color": "A8B9CC", "logo": "c"},
    # Frontend frameworks/libraries
    "React":            {"color": "20232A", "logo": "react"},
    "Angular":          {"color": "DD0031", "logo": "angular"},
    "Next.js":          {"label": "Next.js", "color": "000000", "logo": "next.js"},
    "Redux":            {"color": "593D88", "logo": "redux"},
    "Tailwind CSS":     {"label": "Tailwind_CSS", "color": "38B2AC", "logo": "tailwind-css"},
    "Bootstrap":        {"color": "563D7C", "logo": "bootstrap"},
    "Material-UI":      {"label": "Material--UI", "color": "0081CB", "logo": "material-ui"},
    # Backend
    "Node.js":          {"color": "43853D", "logo": "node.js"},
    "Express.js":       {"color": "404D59", "logo": "express"},
    "Django":           {"color": "092E20", "logo": "django"},
    "Flask":            {"color": "000000", "logo": "flask"},
    "Spring":           {"color": "6DB33F", "logo": "spring"},
    "GraphQL":          {"color": "E10098", "logo": "graphql"},
    "REST API":         {"label": "REST_API", "color": "009688", "logo": "fastapi"},
    # Database
    "MongoDB":          {"color": "4EA94B", "logo": "mongodb"},
    "MySQL":            {"color": "00000F", "logo": "mysql"},
    "PostgreSQL":       {"color": "316192", "logo": "postgresql"},
    "Redis":            {"color": "DC382D", "logo": "redis"},
    "Firebase":         {"color": "FFCA28", "logo": "firebase"},
    "SQLite":           {"color": "07405E", "logo": "sqlite"},
    "Oracle":           {"color": "F80000", "logo": "oracle"},
    # Cloud & DevOps
    "AWS":              {"label": "Amazon_AWS", "color": "232F3E", "logo": "amazon-aws"},
    "Azure":            {"label": "Microsoft_Azure", "color": "0089D6", "logo": "microsoft-azure"},
    "Google Cloud":     {"label": "Google_Cloud", "color": "4285F4", "logo": "google-cloud"},
    "Docker":           {"color": "2496ED", "logo": "docker"},
    "Kubernetes":       {"color": "326CE5", "logo": "kubernetes"},
    "Jenkins":          {"color": "D24939", "logo": "jenkins"},
    "GitHub Actions":   {"label": "GitHub_Actions", "color": "2088FF", "logo": "github-actions"},
    "Terraform":        {"color": "7B42BC", "logo": "terraform"},
    "Nginx":            {"color": "009639", "logo": "nginx"},
    # Tools
    "Git":              {"color": "F05032", "logo": "git"},
    "GitHub":           {"color": "100000", "logo": "github"},
    "GitLab":           {"color": "330F63", "logo": "gitlab"},
    "VS Code":          {"label": "VS_Code", "color": "007ACC", "logo": "visual-studio-code"},
    "IntelliJ IDEA":    {"label": "IntelliJ_IDEA", "color": "000000", "logo": "intellij-idea"},
    "Postman":          {"color": "FF6C37", "logo": "postman"},
    "Jira":             {"color": "0052CC", "logo": "jira"},
    "Linux":            {"color": "FCC624", "logo": "linux"},
    # AI/ML
    "TensorFlow":       {"color": "FF6F00", "logo": "tensorflow"},
    "PyTorch":          {"color": "EE4C2C", "logo": "pytorch"},
    "Scikit-Learn":     {"label": "scikit--learn", "color": "F7931E", "logo": "scikit-learn"},
    "Pandas":           {"color": "150458", "logo": "pandas"},
    "NumPy":            {"color": "013243", "logo": "numpy"},
}

LANG_TO_GROUP: dict[str, str] = {
    "Python": "Backend", "JavaScript": "Frontend", "TypeScript": "Frontend",
    "Java": "Backend", "C++": "Backend", "C#": "Backend", "Go": "Backend",
    "Rust": "Backend", "Kotlin": "Backend", "Swift": "Backend", "Ruby": "Backend",
    "PHP": "Backend", "Dart": "Frontend", "Scala": "Backend", "R": "AI/ML",
    "Jupyter": "AI/ML", "HTML5": "Frontend", "CSS3": "Frontend",
    "Vue.js": "Frontend", "C": "Backend",
}


def get_badge_key(github_language: str) -> str | None:
    """Return the TECH_BADGE_MAP key for a GitHub language name, or None if filtered/unknown."""
    if github_language in FILTERED_LANGUAGES:
        return None
    return GITHUB_LANG_TO_KEY.get(github_language)


def make_badge_url(key: str, style: str = "flat-square") -> str | None:
    """Build a shields.io badge URL for a TECH_BADGE_MAP key. Returns None if key unknown."""
    info = TECH_BADGE_MAP.get(key)
    if not info:
        return None
    label = info.get("label", key.replace(" ", "_"))
    return (
        f"https://img.shields.io/badge/{label}-{info['color']}"
        f"?style={style}&logo={info['logo']}&logoColor=white"
    )
