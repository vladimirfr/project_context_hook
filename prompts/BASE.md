{% if PROJECT %}
Project:
$PROJECT
{% endif %}

{% if RUNTIME %}
Runtime:
$RUNTIME
{% endif %}

{% if ENVIRONMENT %}
Environment:
$ENVIRONMENT
{% endif %}

{% if ARCHITECTURE %}
Architecture (conditional use):
$ARCHITECTURE
{% endif %}

{% if DDEV %}

Execution rules:

- Use host filesystem directly for:
  - file operations (read/write/search)
  - git operations

- Use `ddev exec` only for:
  - PHP and CLI execution
  - Composer
  - Database access
  - WP-CLI (`ddev exec wp ...`)
  - CMS tooling
  - tests requiring container environment

Examples:
- ddev exec wp plugin list
- ddev exec composer install
- ddev exec mysql

Container path translation:
- /var/www/html => .
- /var/www/html/$DOCROOT => ./$DOCROOT
{% endif %}