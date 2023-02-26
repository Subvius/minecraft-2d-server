import uuid

import pygame.time
import lib.functions.api as api
from lib.storage.constants import Constants


class StoryTasks:
    def __init__(self, tasks: dict, ):
        """

        :param tasks: Active player tasks. Can be fetched from api
        """

        self.tasks = tasks
        self.constants = Constants()

    def check_for_completion(self, player, screen):
        """

        :param player: Экземпляр класса Player. Данные текущего пользователя.
        :param screen: Экземпляр класса Screen.
        :return: list[task]
        """
        completed_tasks = list()

        if pygame.time.get_ticks() % 500 == 0:
            for key, value in list(self.tasks.items()):
                task_id = key
                requirements: list[dict] = value.get("requirements")
                completed = True
                for req in requirements:
                    check_type = req.get("type")
                    param = req.get("check_param")

                    if check_type == "location":
                        if not eval(f"player.{param}"):
                            completed_tasks = False

                if completed:
                    completed_tasks.append(value)

        return completed_tasks

    def get_tasks(self):
        return self.tasks

    def add_task(self, nickname, fraction: str, questor: str, requirements: list[dict], title: str, task_type: str,
                 short_desc: str = "", deadline: int = -1, rewards: list[dict] = []):
        """

        :param rewards: Награда-(ы), которые получит игрок, когда выполнит задание. По умолчанию - ничего.
        :param nickname: Player data. Экземпляр класса Player
        :param fraction: Фракция квестодателя или посредника.
        :param questor: Имя квестодателя.
        :param requirements: Необходимые условия выполнения. (Необходимо выполнить всё для выполнения).
        :param title: Заголовок, название задания. Желательно небольше 20 символов.
        :param task_type: Тип задания.
        :param short_desc: Короткое описание задания.
        :param deadline: Время отведенное на выполнение. Timestamp реального времени. Указать -1 в случае, когда
         задание бессрочно
        :return: {success: bool, "E": if there are any error}
        """

        task_data = {
            "deadline": deadline,
            "fraction": fraction,
            "id": uuid.uuid4().__str__(),
            "questor": questor,
            "requirements": requirements,
            "short_desc": short_desc,
            "title": title,
            "type": task_type,
            "rewards": rewards
        }
        res = api.post_data(self.constants.api_url + f"player/?player={nickname}&add_task=true", task_data)

        if res.get("success", False):
            self.tasks.update({
                task_data.get("id"): task_data
            })

        return res

    def update_task(self, task_id: str, nickname, **kwargs):
        """
        Update player's story task.

        :param nickname: Player data. Экземпляр класса Player
        :param task_id: ID of the task to update
        :param kwargs: Params to update
        :return: {success: bool, "E": if there are any error}
        """

        task_data = kwargs
        task_data.update(
            {
                "id": task_id
            }
        )

        res = api.post_data(self.constants.api_url + f"player/?player={nickname}&update_task=true", task_data)

        if res.get("success", False):
            self.tasks.update({
                task_data.get("id"): task_data
            })

        return res

    def complete_task(self, task_id: str, nickname):
        """

        :param nickname: Player data. Экземпляр класса Player
        :param task_id: ID of the task to compete
        :return: {success: bool, "E": if there are any error}
        """

        task_data = {
            "id": task_id
        }

        res = api.post_data(self.constants.api_url + f"player/?player={nickname}&complete_task=true", task_data)

        if res.get("success", False):
            self.tasks.update({
                task_data.get("id"): task_data
            })

        return res
