import praw
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

# Set up your Reddit API credentials
reddit = praw.Reddit(
        client_id='X',
        client_secret='X',
        user_agent='X'
    )


def fetch_comments(reddit_link):
    try:
        submission = reddit.submission(url=reddit_link)
        submission.comments.replace_more(limit=None)
        comments = submission.comments.list()
        return submission, comments  # Return both submission and comments
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch comments: {e}")
        return None, []


def display_comments(comments):
    user_comments = {}
    for comment in comments:
        author = str(comment.author) if comment.author else "Deleted"
        # Ignore comments by AutoModerator
        if author == "AutoModerator":
            continue
        if author not in user_comments:
            user_comments[author] = []
        user_comments[author].append(comment)
    return user_comments


def update_users(event):
    selected_user = user_dropdown.get()
    comments_list.delete(0, tk.END)

    # Clear the comment display when switching users
    comment_display.config(state=tk.NORMAL)
    comment_display.delete(1.0, tk.END)
    comment_display.config(state=tk.DISABLED)

    if selected_user in user_comments:
        for i, comment in enumerate(user_comments[selected_user]):
            read_status = 'read' if selected_user in read_comments and i in read_comments[selected_user] else 'unread'
            display_text = f"{i + 1}. {comment.body[:50]}... ({read_status})"
            comments_list.insert(tk.END, display_text)

        # Automatically select and display the first comment
        if user_comments[selected_user]:
            comments_list.selection_set(0)  # Select the first comment
            update_comments(None)


def update_comments(event):
    selected_user = user_dropdown.get()
    selected_index = comments_list.curselection()

    if selected_user in user_comments and selected_index:
        comment_index = selected_index[0]
        comment = user_comments[selected_user][comment_index]

        comment_display.config(state=tk.NORMAL)
        comment_display.delete(1.0, tk.END)
        comment_display.insert(tk.END, comment.body)

        # Highlight the entire comment in green if marked as read
        if selected_user in read_comments and comment_index in read_comments[selected_user]:
            comment_display.tag_add("read", "1.0", tk.END)  # Add the tag from the start to the end
            comment_display.tag_configure("read", background="lightgreen")  # Set the background to green

        comment_display.config(state=tk.DISABLED)


def mark_as_read():
    selected_index = comments_list.curselection()
    selected_user = user_dropdown.get()

    if selected_user in user_comments and selected_index:
        comment_index = selected_index[0]

        # Mark the comment as read
        if selected_user not in read_comments:
            read_comments[selected_user] = set()
        read_comments[selected_user].add(comment_index)

        # Call update_users(None) to refresh the user display
        update_users(None)

        # Restore the selection of the comment
        comments_list.selection_clear(0, tk.END)
        comments_list.selection_set(comment_index)
        comments_list.activate(comment_index)  # Ensure the same comment stays active
        comments_list.see(comment_index)  # Scroll to the comment if necessary

        # Ensure the top text box updates with the correct comment
        update_comments(None)


def open_in_browser():
    selected_user = user_dropdown.get()
    selected_index = comments_list.curselection()

    if selected_user in user_comments and selected_index:
        comment_index = selected_index[0]
        comment = user_comments[selected_user][comment_index]

        # Get the permalink for the selected comment and open it in the browser
        comment_link = f"https://reddit.com{comment.permalink}"
        webbrowser.open(comment_link)


# GUI setup
root = tk.Tk()
root.title("CMHoC Comments Reader")
logo = tk.PhotoImage(file="logoblue.png")

# Set the logo as the window icon
root.iconphoto(False, logo)
# Input for Reddit link
link_label = tk.Label(root, text="Enter Reddit Link:")
link_label.grid(row=0, column=0, padx=10, pady=5)

link_entry = tk.Entry(root, width=50)
link_entry.grid(row=0, column=1, padx=10, pady=5)

# Fetch comments button
fetch_button = tk.Button(root, text="Fetch Comments", command=lambda: fetch_and_display())
fetch_button.grid(row=0, column=2, padx=10, pady=5)

# Dropdown for users
user_label = tk.Label(root, text="Select User:")
user_label.grid(row=1, column=0, padx=10, pady=5)

user_dropdown = ttk.Combobox(root)
user_dropdown.bind("<<ComboboxSelected>>", update_users)
user_dropdown.grid(row=1, column=1, padx=10, pady=5)

# Listbox for comments
comments_list = tk.Listbox(root, width=80, height=10)
comments_list.grid(row=2, column=0, columnspan=3, padx=10, pady=5)
comments_list.bind("<<ListboxSelect>>", update_comments)  # Bind click event to navigate

# Scrollbar for comment display
scrollbar = tk.Scrollbar(root)
scrollbar.grid(row=3, column=2, sticky='ns')

# Text widget to display selected comment
comment_display = tk.Text(root, wrap=tk.WORD, width=80, height=15, yscrollcommand=scrollbar.set, state=tk.DISABLED)
comment_display.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

scrollbar.config(command=comment_display.yview)

# Button to mark as read
read_button = tk.Button(root, text="Mark as Read", command=mark_as_read)
read_button.grid(row=4, column=1, padx=10, pady=5, sticky='w')

# Button to open the comment in the browser
browser_button = tk.Button(root, text="Open in Browser", command=open_in_browser)
browser_button.grid(row=4, column=1, padx=10, pady=5, sticky='e')


def fetch_and_display():
    reddit_link = link_entry.get()
    submission, comments = fetch_comments(reddit_link)
    global user_comments
    user_comments = display_comments(comments)

    if user_comments:
        user_dropdown['values'] = list(user_comments.keys())
        user_dropdown.current(0)  # Select the first user by default
        update_users(None)  # Update the comment list for the first user
    else:
        messagebox.showinfo("No comments", "No comments were fetched.")


user_comments = {}
read_comments = {}

root.mainloop()
