import praw
import tkinter as tk
from tkinter import ttk

# Set up your Reddit API credentials
reddit = praw.Reddit(
        client_id='X',
        client_secret='X',
        user_agent='X'
    )


def fetch_comments(reddit_link):
    submission = reddit.submission(url=reddit_link)
    submission.comments.replace_more(limit=None)
    comments = submission.comments.list()
    return comments


def display_comments(comments):
    user_comments = {}
    for comment in comments:
        author = str(comment.author) if comment.author else "Deleted"
        # Ignore comments by AutoModerator
        if author == "AutoModerator":
            continue
        if author not in user_comments:
            user_comments[author] = []
        user_comments[author].append(comment.body)
    return user_comments


def update_users(event):
    selected_user = user_dropdown.get()
    comments_list.delete(0, tk.END)
    comments_dropdown['values'] = []

    # Clear the comment display when switching users
    comment_display.config(state=tk.NORMAL)
    comment_display.delete(1.0, tk.END)
    comment_display.config(state=tk.DISABLED)

    if selected_user in user_comments:
        for i, comment in enumerate(user_comments[selected_user]):
            read_status = 'read' if selected_user in read_comments and i in read_comments[selected_user] else 'unread'
            display_text = f"{i + 1}. {comment[:50]}... ({read_status})"  # Show a preview of 50 characters
            comments_list.insert(tk.END, display_text)

        comments_dropdown['values'] = list(range(1, len(user_comments[selected_user]) + 1))  # Start at 1 for selection

        # Highlight read comments in the list
        for i in range(len(user_comments[selected_user])):
            if selected_user in read_comments and i in read_comments[selected_user]:
                comments_list.itemconfig(i, {'bg': 'lightgreen'})  # Change color to green


def update_comments(event):
    selected_user = user_dropdown.get()
    selected_index = comments_dropdown.get()

    if selected_user in user_comments and selected_index:
        comment_index = int(selected_index) - 1  # Adjust for 0-based index
        comment_body = user_comments[selected_user][comment_index]

        comment_display.config(state=tk.NORMAL)  # Enable the comment display for editing
        comment_display.delete(1.0, tk.END)  # Clear previous text
        comment_display.insert(tk.END, comment_body)  # Insert the full comment

        # Highlight in green if marked as read
        if selected_user in read_comments and comment_index in read_comments[selected_user]:
            comment_display.tag_configure("read", background="lightgreen")
            comment_display.insert(tk.END, "\n", "read")  # Add a newline for formatting
        comment_display.config(state=tk.DISABLED)  # Disable editing


def mark_as_read():
    selected_index = comments_dropdown.get()
    selected_user = user_dropdown.get()

    if selected_user in user_comments and selected_index:
        # Mark the comment as read
        if selected_user not in read_comments:
            read_comments[selected_user] = set()
        read_comments[selected_user].add(int(selected_index) - 1)  # Adjust for 0-based index
        comments_list.itemconfig(int(selected_index) - 1, {'bg': 'lightgreen'})  # Change color to green
        update_comments(None)  # Refresh to update the comment display


# GUI setup
root = tk.Tk()
root.title("Reddit Comment Viewer")

# Input for Reddit link
link_label = tk.Label(root, text="Enter Reddit Link:")
link_label.pack()

link_entry = tk.Entry(root, width=50)
link_entry.pack()

# Fetch comments button
fetch_button = tk.Button(root, text="Fetch Comments", command=lambda: fetch_and_display())
fetch_button.pack()

# Dropdown for users
user_label = tk.Label(root, text="Select User:")
user_label.pack()

user_dropdown = ttk.Combobox(root)
user_dropdown.bind("<<ComboboxSelected>>", update_users)
user_dropdown.pack()

# Listbox for comments
comments_list = tk.Listbox(root, width=80, height=10)
comments_list.pack()

# Dropdown for comments
comments_label = tk.Label(root, text="Select Comment:")
comments_label.pack()

comments_dropdown = ttk.Combobox(root)
comments_dropdown.bind("<<ComboboxSelected>>", update_comments)
comments_dropdown.pack()

# Scrollbar for comment display
scrollbar = tk.Scrollbar(root)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Text widget to display selected comment
comment_display = tk.Text(root, wrap=tk.WORD, width=80, height=15, yscrollcommand=scrollbar.set, state=tk.DISABLED)
comment_display.pack(expand=True, fill=tk.BOTH)  # Allow the text box to expand

scrollbar.config(command=comment_display.yview)

# Button to mark as read
read_button = tk.Button(root, text="Mark as Read", command=mark_as_read)
read_button.pack()


def fetch_and_display():
    reddit_link = link_entry.get()
    comments = fetch_comments(reddit_link)
    global user_comments
    user_comments = display_comments(comments)

    user_dropdown['values'] = list(user_comments.keys())
    user_dropdown.current(0)  # Select the first user by default
    update_users(None)  # Update the comment list for the first user


user_comments = {}
read_comments = {}  # Dictionary to track read comments per user

root.mainloop()
