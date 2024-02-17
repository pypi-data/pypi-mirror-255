import logging
import textwrap
from typing import Optional

import requests
import ujson as json
from clustaar.schemas.models import (Button, Card, GoToAction, JumpToAction,
                                     OpenURLAction, QuickReply,
                                     SendCardsAction, SendQuickRepliesAction,
                                     SendTextAction, StepTarget, StoryTarget,
                                     WaitAction)


class Client:
    """Class used to comunicates with the spellz api"""

    def __init__(self, spellz_token: str, spellz_domain: Optional[str] = None) -> None:
        """
        Args:
            spellz_token: it corresponds to their x-api-key
            spellz_domain: the domaine (prod/staging)
        """
        self._spellz_token = spellz_token
        self._spellz_domain = spellz_domain or "https://backend.clustaar.io"

        # TODO add quick replies extractor here when ready
        self._clustaar_extractor = {
            "text": self._extract_send_text_action,
            "cards": self._extract_send_cards_action,
            "go_to_step": self._extract_jump_to_action,
            "go_to_story": self._extract_jump_to_action,
            "typing": self._extract_wait_action,
            "quick_replies": self._extract_send_quick_replies_action,
        }

        self._logger = logging.getLogger(__name__)

    def reply(
        self,
        interlocutor_id: str,
        message: str,
        path: Optional[str] = "interaction",
        session: Optional[dict] = None,
        custom_attributes: Optional[dict] = None,
        extra: Optional[dict] = None,
        type: Optional[str] = "knowledge",
    ) -> list:
        """
        Function used to ask a reply to the spellz bot/LLM.

        Args:
            interlocutor_id: the clustaar interlocutor id
            message: the message sended
            session: the clustaar session values
            extra: extra infos if needed
        """
        actions = []
        confidence = "low"

        data = {
            "query": message,
            "sessionValues": session.values,
            "customAttributes": custom_attributes,
            "extraInfos": extra,
            "sameContext": False,
            "type": type
        }

        self._logger.debug(
            f'Send message "{message}" to the spellz reply handler with interlocutor ID = {interlocutor_id}'
        )

        res = self._post_spellz(f"/bots/interlocutor/{interlocutor_id}/{path}", data)

        if res.status_code == 200:
            json_res = res.json()
        else:
            self._logger.error(
                f"Invalid status code '{res.status_code}' with reply: {res.text}"
            )

            return [], confidence

        confidence = json_res["confidence"]

        if "sessionValues" in json_res:
            for k, v in json_res["sessionValues"].items():
                session.values[k] = v

        for s_action in json_res["actions"]:
            try:
                action = self._clustaar_extractor[s_action["type"]](s_action)
            except KeyError:
                type = s_action["type"]

                self._logger.exception(
                    f'Putain pierre pourquoi tu me passe des types pas gérés comme ["{type}"]!!!'
                )

            actions.append(action)

        return actions, confidence

    def get_resource(
        self,
        interlocutor_id: str,
        resource_id: str,
        path: Optional[str] = "resources",
        session: Optional[dict] = None,
        custom_attributes: Optional[dict] = None,
        extra: Optional[dict] = None,
    ) -> list:
        """
        Function used to ask a reply to the spellz bot/LLM.

        Args:
            interlocutor_id: the clustaar interlocutor id
            ressource_id: the ressource id targeted
            path: the routes path
            session: the clustaar session values
            custom_attributes: user attributes
            extra: extra infos if needed
        """
        actions = []
        confidence = "low"

        data = {
            "sessionValues": session.values,
            "customAttributes": custom_attributes,
            "extraInfos": extra,
        }

        self._logger.debug(
            f'Getting resource "{resource_id}" to the spellz resource handler with interlocutor ID = {interlocutor_id}'
        )

        res = self._post_spellz(
            f"/bots/interlocutor/{interlocutor_id}/interaction/{path}/{resource_id}",
            data,
        )

        if res.status_code == 200:
            json_res = res.json()
        else:
            self._logger.error(
                f"Invalid status code '{res.status_code}' with reply: {res.text}"
            )

            return [], confidence

        confidence = json_res["confidence"]

        if "sessionValues" in json_res:
            for k, v in json_res["sessionValues"].items():
                session.values[k] = v

        for s_action in json_res["actions"]:
            try:
                action = self._clustaar_extractor[s_action["type"]](s_action)
            except KeyError:
                type = s_action["type"]

                self._logger.exception(
                    f'Putain pierre pourquoi tu me passe des types pas gérés comme ["{type}"]!!!'
                )

            actions.append(action)

        return actions, confidence

    def _extract_send_text_action(self, action: dict):
        """Used to extract send_text_action from spell action

        Args:
            action: an action as dict
        """
        return SendTextAction(text=action["text"], alternatives=[action["text"]])

    def _extract_wait_action(self, action: dict):
        """Used to extract wait_ction from spell action

        Args:
            action: an action as dict
        """
        return WaitAction(duration=action["duration"])

    def _extract_jump_to_action(self, action: dict):
        """Used to extract jump_to_action from spell action

        Args:
            action: an action as dict
        """
        # TODO demander a l'homme cailloux d'ajouter le name de la step dans l'action (a voir pour ajouter des connections)

        kind = action.get("type", "go_to_step")

        if kind == "go_to_step":
            return JumpToAction(
                default_target=StepTarget(
                    step_id=action.get("id"), name=action.get("name") or "Pierre le cailloux plat"
                ),
                connections=[],
            )
        return JumpToAction(
            default_target=StoryTarget(
                story_id=action.get("id"), name=action.get("name") or "Pierre le cailloux plat"
            ),
            connections=[],
        )

    def _extract_send_cards_action(self, action: dict):
        """Used to extract send_cards_action from spell action

        Args:
            action: an action as dict
        """
        cards = []

        for card in action["cards"]:
            buttons = []

            for button in card["buttons"]:
                title = textwrap.shorten(button["label"], 20)

                buttons.append(
                    Button(title=title, action=OpenURLAction(url=button["value"]))
                )
            card = Card(
                title=card["title"],
                subtitle=card["subtitle"],
                buttons=buttons,
                image_url=card.get("imageURL", ""),
                url=card.get("url", ""),
                alt=card.get("alt", ""),
            )

            cards.append(card)

        return SendCardsAction(cards=cards)

    def _extract_send_quick_replies_action(self, action: dict):
        """Used to extract send_quick_replies_action from spell action

        Args:
            action: an action as dict
        """

        buttons = []
        message = action.get("text")

        for button in action["buttons"]:
            try:
                label = button.get("label")
                type = button.get("type")
                value = button.get("value")
                sessionValues = button.get("sessionValues", {})

                if type == "go_to_step":
                    step = StepTarget(step_id=value, name=label)
                    action = GoToAction(target=step, session_values=sessionValues)
                else:
                    raise Exception("Type not handled")

                button = QuickReply(title=label, action=action)
                buttons.append(button)
            except KeyError:
                self._logger.exception(
                    f'Putain Axel, tu gère pas encore le type ["{type}"] ??!!'
                )

        if buttons == []:
            raise Exception("Empty buttons")

        return SendQuickRepliesAction(message=message, buttons=buttons)

    def _post_spellz(self, url: str, data: dict):
        """
        Fonction used to send an HTTP request to spellz

        Args:
            url: the targeted url point
            data: the data to send (have to be jsonifiable)
        """
        full_url = self._spellz_domain + url

        data = json.dumps(data)

        self._logger.debug(f'Send post HTTP request to "{full_url}" with body: {data}')

        res = requests.post(
            full_url,
            data=data,
            headers={
                "x-api-key": self._spellz_token,
                "content-type": "application/json",
            },
        )

        self._logger.debug(
            f'Successful send of a post HTTP request to "{full_url}" status {res.status_code} with body: {res.text}'
        )

        return res
