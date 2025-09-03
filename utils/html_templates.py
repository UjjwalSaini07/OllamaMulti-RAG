css = """
<style>
    /* User Chat Bubble */
    .user-bubble {
        background-color: var(--user-msg-bg, #2b313e);
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        max-width: 80%;
        align-self: flex-end;
        word-wrap: break-word;
    }

    /* AI Chat Bubble */
    .ai-bubble {
        background-color: var(--ai-msg-bg, #475063);
        color: white;
        padding: 0.75rem 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        max-width: 80%;
        align-self: flex-start;
        word-wrap: break-word;
    }

    /* Chat Container (flex layout) */
    .chat-container {
        display: flex;
        flex-direction: column;
    }

    /* Sidebar width override */
    section[data-testid="stSidebar"] {
        width: 380px !important;
    }
</style>
"""
