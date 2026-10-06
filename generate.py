from gateway import chat


def generate(hits, problem):
    lines = []
    for hit in hits:
        lines.append(f"[{hit['id']} p.{hit['page']}] {hit['text']}")
    user = f"问题：{problem}\n\n证据：\n" + "\n".join(lines)
    system = "请你只能根据证据、要写出处、不够就说不知道为准则回答用户的问题"
    return chat(user, system)