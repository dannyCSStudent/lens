class NotificationType:
    POST_REPLY = "post_reply"
    POST_LIKE = "post_like"
    REPLY_REPLY = "reply_reply"
    MENTION = "mention"
    FOLLOW = "follow"
    SYSTEM = "system"

    # moderation / system events
    CONTENT_MODERATED = "content_moderated"
    EVIDENCE_ADDED = "evidence_added"
