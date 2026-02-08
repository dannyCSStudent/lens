def build_reply_tree(replies):
    by_id = {r.id: {**r.__dict__, "children": []} for r in replies}
    roots = []

    for reply in by_id.values():
        parent_id = reply["parent_reply_id"]
        if parent_id and parent_id in by_id:
            by_id[parent_id]["children"].append(reply)
        else:
            roots.append(reply)

    return roots
