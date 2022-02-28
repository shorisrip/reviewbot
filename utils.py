import re
import os
from datetime import date
from hackmd import get_note, update_note


def add_new_review(review, content):
    if not re.search(re.escape(review), content):
        today = date.today()
        date_heading = "## " + today.strftime("%b %d, %Y") + "\n"
        index = content.find(date_heading)
        # If no entry for today's date
        if index == -1:
            # Check if we have tags
            is_tags = re.search("tags: `.*`\n", content)
            if is_tags:
                # Insert new date after tags
                date_index = is_tags.regs[0][1]
            else:
                # Check if we have heading
                is_title = re.search("^#[ \t]+.*\n", content)
                if is_title:
                    # Insert new date after main heading
                    date_index = is_title.regs[0][1]
                else:
                    # idk, insert at the beginning?
                    date_index = 0
            new_content = content[:date_index] + "\n" + date_heading +\
                          '\n* ' + review + "\n" + content[date_index:]
            return new_content
        new_content = content[:(index + len(date_heading))] + '\n* ' + review + "\n" \
                      + content[(index + len(date_heading)):]
        return new_content
    return content


def write_to_destination(review):
    note_id = os.getenv("note_id")
    content = get_note(note_id)
    if content is not None:
        new_content = add_new_review(review, content)
        result = update_note(note_id, new_content)
        return result
    return None
