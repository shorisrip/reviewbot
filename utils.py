import re
import os
import datetime
import dateutil.parser as dparser
from hackmd import get_note, update_note

def add_content(index, old_content, new_string):
    new_content = old_content[:index] + "\n" + new_string + old_content[index:]
    return new_content

def update_review_list(review, content,topic=None, to_date=datetime.date.today()):
    if topic:
        review = review + " (" + topic + ")"
    # Check if we have main heading
    is_title = re.search("^#[ \t]+.*\n", content)
    if not is_title:
        title_index = 0
        title_heading = "# Review List from " + to_date.strftime("%b %d, %Y") \
                        + " onwards"
        content = add_content(title_index, content, title_heading)
        tag_index = len(title_heading)
    else:
        # find_title = re.findall("^#[ \t]+.*\n", content)
        tag_index = is_title.regs[0][1]
        # tag_index = len(find_title[0])
    # Check if we have tags
    is_tags = re.search("tags: `.*`\n", content)
    if not is_tags:
        tag_heading = "###### tags: `ruck_rover`"
        content = add_content(tag_index, content, tag_heading)
        date_index = tag_index + len(tag_heading)
    else:
        date_index = is_tags.regs[0][1]
    # Check if date heading is present
    date_syntax = to_date.strftime("%b %d, %Y") + "\n"
    date_heading = "## " + date_syntax
    is_date = re.search(re.escape(date_heading), content)
    if not is_date:
        content = add_content(date_index, content, date_heading)
        review_index = date_index + len(date_heading)
    else:
        review_index = is_date.regs[0][1]
    # Check if review is present at all in the whole doc
    is_review_present = re.search(re.escape(review), content)
    # Check if review is persent under current date
    if is_review_present:
        # Section of note after the last H2 heading before the review
        section_of_note = content.split(review)[0].split("\n## ")[-1]
        index = section_of_note.find(date_syntax)
        if index == -1:
            is_review_present = False
    if not is_review_present:
        content = add_content(review_index, content, "* " + review)
        return content
    else:
        print("Review is already present")
        return content


def add_new_review(review, content):
    new_content = update_review_list(review, content)
    return new_content


def move_review_to_date(review, content, to_date):
    pass


def add_review_under_topic(review, content, topic):
    update_review_list(review, content, topic)


def find_links(msg):
    patches_regex = r"https?://\S+"
    links_found = re.findall(patches_regex, msg, re.IGNORECASE)
    return links_found

def find_topic(msg):
    reviews = []
    patches_regex = r"https?://\S+"
    topic_regexp = r"https?://\S+ ?\(topic:.*\)"
    reviews_parts = re.findall(r"(https?://\S+ ?\(topic:.*\)|https?://\S+)", msg, re.IGNORECASE)
    for item in reviews_parts:
        topic_found =  re.findall(topic_regexp, item, re.IGNORECASE)
        review_found = re.findall(patches_regex, msg, re.IGNORECASE)
        reviews.append({"topic": topic_found[0], "patch": review_found[0]})
    return reviews


def find_date(msg):
    date_found = None
    try:
        date_found = dparser.parse(msg, fuzzy=True, dayfirst=True)
    except Exception as exp:
        print("Unrecognized datetime/ datetime not found in comment: ", msg, "Exp: ", str(exp))
    if date_found:
        return date_found
    return datetime.date.today() + datetime.timedelta(days=1)


def handle_new_review_request(msg, topic=None):
    return_msg_counter = 0
    failed_to_add = []
    return_msg = ""
    links_found = find_links(msg)
    for link in links_found:
        if link[-1] in [",", ";", " "]:
            link = link[:-1]
        print(str(datetime.datetime.now()), " : ", link)
        # Send to hackmd
        if topic:
            result = write_to_destination(link, "add_review_under_topic", topic)
        else:
            result = write_to_destination(link, "new_review")
        if not result:
            failed_to_add = failed_to_add + link + " "
        else:
            return_msg_counter += 1
    if return_msg_counter > 0:
        return_msg = "I have added " + str(return_msg_counter) + " to the review list"
    if failed_to_add:
        return_msg = return_msg + "I could not add: " + (", ".join(failed_to_add))
    return return_msg


def handle_new_review_request_with_topic(msg):
    review_with_topic = find_topic(msg)
    for item in review_with_topic:
        print(str(datetime.datetime.now()), " : ", item["patch"], " topic: ", item["topic"])
        # Send to hackmd
        result = write_to_destination(item["patch"], "add_review_under_topic", item["topic"])
    result = handle_new_review_request(msg, review_with_topic)
    return result

def handle_move_review(msg):
    links_found = find_links(msg)
    date_found = find_date(msg)
    for link in links_found:
        print("Move request: ", str(datetime.datetime.now()), " : ", link)
        # Send to hackmd
        result = write_to_destination(link, "move_review", date_found)
        if not result:
            return"I could not add the review to Review List"
        return result

def write_to_destination(review, action_type="new_review", topic=None, to_date=datetime.date.today() + datetime.timedelta(days=1)):
    note_id = os.getenv("note_id")
    content = get_note(note_id)
    if content is not None:
        if action_type == "new_review":
            new_content = add_new_review(review, content)
            result = update_note(note_id, new_content)
            return result
        if action_type == "move_review":
            new_content = move_review_to_date(review, content, to_date)
            result = update_note(note_id, new_content)
            return result
        if action_type == "add_review_under_topic":
            new_content = add_review_under_topic(review, content, topic)
            result = update_note(note_id, new_content)
            return result
    return None
