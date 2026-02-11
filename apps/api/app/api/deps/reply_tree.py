async def build_reply_tree(replies):
    reply_map = {r.id: r for r in replies}
    tree = []
    for reply in replies:
        if reply.parent_reply_id:
            parent = reply_map.get(reply.parent_reply_id)
            if parent:
                parent.children.append(reply)
        else:
            tree.append(reply)
    return tree
