def Chat(prompt, role="user"):
    return {
        "role": role,
        "content": prompt,
       
    }

def WorkflowChat(prompt, model=None, role="user"):
    return {
        "role": role,
        "content": prompt,
        "model": model
    }

def UserChat(prompt, model=None):
    return Chat(prompt, "user")

def AssistantChat(prompt, model=None):
    return Chat(prompt, role="assistant")

def SystemChat(prompt, model=None):
    return Chat(prompt, role="system")