title: "[Bug] "
body:
  - type: textarea
    id: description
    attributes:
      label: Describe the bug
      description: A clear and concise description of what the bug is.
      placeholder: Bug description
    validations:
      required: true
  - type: textarea
    id: bug-reproduce
    attributes:
      label: To Reproduce
      description: Tell us how to reproduce the bug.
      value: "Steps to reproduce the behavior:\n1. Go to '...'\n2. Click on '....'\n3. Scroll down to '....'\n4. See error"
    validations:
      required: false
  - type: dropdown
    id: version
    attributes:
      label: Version
      description: What version of our software are you running?
      multiple: false
      options:
        - 1.6.0
        - 1.5.4
        - Other (specify in description)
      default: 0
    validations:
      required: true
  - type: dropdown
    id: resolution
    attributes:
      label: In-game resolution
      multiple: false
      options:
        - 1680x1050
        - 1920x1080
        - 2560x1440
        - Other (specify in description)
    validations:
      required: true
  - type: checkboxes
    id: multi-screen
    attributes:
      label: Multiple monitors
      options:
        - label: Do you use multiple monitors?
          required: false
  - type: textarea
    id: logs
    attributes:
      label: Relevant log output
      description: Please copy and paste any relevant log output.
      render: shell