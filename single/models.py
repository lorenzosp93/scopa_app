from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import related
from django.db.models.fields.related import ForeignKey

# Create your models here.

RANK = (
    (0, "Bastoni"),
    (1, "Spade"),
    (2, "Denari"),
    (3, "Coppe"),
)

class Card(models.Model):
    class Meta:
        unique_together = ['value', 'rank']
    
    value = models.IntegerField(
        choices=range(1,11),
        editable=False,
    )

    rank = models.IntegerField(
        choices=RANK,
        verbose_name="Semi",
        editable=False,
    )

class Match(models.Model):
    class Meta:
        pass

    @property
    def users(self):
        pass

    @property
    def winner(self):
        pass



PRIMIERA_MAP = {
    7: 21,
    6: 18,
    1: 16,
    5: 15,
    4: 14,
    3: 13,
    2: 12,
    8: 10,
    9: 10,
    10: 10,
}

def primiera_score(captures:list[Card]) -> int:
    score = 0
    oppscore = 0
    for r in RANK:
        vals = captures.filter(rank=r).values_list('value')
        score += max(
            PRIMIERA_MAP[val] for val in vals
        )
        oppscore += max(
            PRIMIERA_MAP[key] for key in PRIMIERA_MAP.keys() if key not in vals
        )
    return score > oppscore

def denari_score(captures:list[Card]) -> int:
    return captures.filter(rank=2).count() > 5

def settoro_score(captures:list[Card]) -> int:
    return captures.filter(rank=2, value=7).count()

def carte_score(captures:list[Card]) -> int:
    return captures.count() > 20

class Round(models.Model):
    class Meta:
        pass
    
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="rounds",
    )

    @property
    def winner(self):
        return max(self.score, key=self.score.get)

    @property
    def score(self) -> dict[str, int]:
        scores = {}
        for u in self.plays.values('user').distinct():
            plays = self.plays.filter(user=u)
            cap = plays.values('cards_captured')
            scores.update(
                {
                    u.username: {
                        "primiera": primiera_score(cap),
                        "denari": denari_score(cap),
                        "settoro": settoro_score(cap),
                        "carte": carte_score(cap),
                        "scope": plays.filter(scopa=True).count(),
                    }
                }
            )
        return {u: sum(scores[u].values()) for u in scores.keys()}

class Play(models.Model):
    class Meta:
        pass

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="plays",
    )

    round = models.ForeignKey(
        Round,
        on_delete=models.CASCADE,
        related_name="plays"
    )

    card_played = models.ForeignKey(
        Card,
        on_delete=models.SET_NULL,
        related_name="played_in",
    )

    cards_captured = models.ManyToManyField(
        Card,
        related_name="captured_in",
    )

    scopa = models.BooleanField(
        verbose_name="Scopa",
    )
