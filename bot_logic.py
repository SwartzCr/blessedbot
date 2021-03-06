from twython import Twython
import json

def auth():
    with open("access.json", 'r') as f:
        db = json.load(f)
    return Twython(db["API_Key"], db["API_Secret"], db["Access_Token"], db["Access_Token_Secret"])

def load():
    with open("queue.json", 'r') as f:
        queue = json.load(f)
    with open("info.json", 'r') as fi:
        info = json.load(fi)
    return queue, info

def dump(queue, info):
    with open("queue.json", 'w') as f:
        json.dump(queue, f)
    with open("info.json", 'w') as fi:
        json.dump(info, fi)

def respond(twitter, top_tweet):
    text = top_tweet["text"]
# remove all hash tags
    text = text.split("#")[0] + "#BLESSED"
    twitter.update_status(status=text)


def main():
    twitter = auth()
    queue, info = load()
    tweets = twitter.search(q="#fml", result_type="recent", since_id=info["sinceid"], count='100')
    info["sinceid"] = tweets["search_metadata"]["max_id"]
    triggers = ("#fml", "#FML")
    to_add = [tweet for tweet in tweets["statuses"] if not tweet["retweeted"] and 
                                                       not tweet.has_key("retweeted_status") and
                                                       not tweet["in_reply_to_status_id"] and
                                                       tweet["entities"]["urls"] == []]
    to_add = [tweet for tweet in to_add if "#fml" in tweet["text"]
                                        or "#FML" in tweet["text"]
                                        and "@" not in tweet["text"]]
    queue = queue + to_add
    mx = max(len(to_add), 20)
    if len(queue) > mx:
        queue = queue[-mx:]
    if len(queue) > 0:
        respond(twitter, queue.pop())
    dump(queue, info)

#run on cron every minute
if __name__ == "__main__":
    main()
