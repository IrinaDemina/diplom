import requests
import time
import json

TOKEN = "7b23e40ad10e08d3b7a8ec0956f2c57910c455e886b480b7d9fb59859870658c4a0b8fdc4dd494db19099"
VERSION = "5.74"
API = "https://api.vk.com/method/"


def get_vk_data(api, method, params):
    while True:
        try:
            response = requests.get(f"{api}{method}", params=params)
            response.raise_for_status()
            response = response.json()
            return response["response"]
        except Exception:
            error = response["error"]["error_code"]
            if error == 6:
                time.sleep(3)
                continue
            else:
                print(f'Ошибка {response["error"]["error_msg"]}')
                return dict({"items":""})


def fined_groups(params, id):
    params.update(dict(
        user_id=id,
        fields=["name", "members_count"],
        count=1000,
        extended=1
    ))
    groups = get_vk_data(API, "groups.get", params)["items"]
    return groups


def fined_friends(params, id):
    params.update(user_id=id)
    friends = get_vk_data(API, "friends.get", params)["items"]
    activated_friends = [i["id"] for i in friends if "deactivated" not in i]
    return activated_friends


def get_result_groups(params, friends, groups):
    all_friends_groups = set()
    groups_id = [gr["id"] for gr in groups]
    for i, friend in enumerate(friends):
        friend_groups = fined_groups(params, friend)
        print(f"Осталось обработать {len(friends)-i} друзей")
        friend_groups_id = [gr["id"] for gr in friend_groups]
        all_friends_groups = all_friends_groups.union(friend_groups_id)
    groups_result = set(groups_id).difference(all_friends_groups)
    return groups_result


def user_name(params):
    user = input("Введите ID или имя пользователя VK: ")
    if user.isdigit():
        user_id = user
    else:
        params.update(screen_name=user)
        user_id = get_vk_data(API, "utils.resolveScreenName", params)["object_id"]
    return user_id


def save_result_json(result):
    with open("groups.json", "w", encoding="utf8") as f:
        json.dump(result, f, ensure_ascii=False)


def main():
    params = dict(v=VERSION, access_token=TOKEN)
    user_id = user_name(params)
    groups = fined_groups(params, user_id)
    friends = fined_friends(params, user_id)
    groups_result = get_result_groups(params, friends, groups)

    result = []
    for gr in groups:
        if gr["id"] in groups_result:
            result.append({k: v for k, v in gr.items() if (k in ("name", "id", "members_count"))})
    save_result_json(result)
    print("Результат сохранен в файле groups.json")


if __name__ == "__main__":
    main()
