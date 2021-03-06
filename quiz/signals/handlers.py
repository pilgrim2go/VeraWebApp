from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver

from jobboard.handlers.oracle import OracleHandler
from pipeline.tasks import candidate_level_up
from quiz.models import ExamPassed, AnswerForVerification, ActionExam
from quiz.tasks import ProcessExam, VerifyAnswer


@receiver(post_save, sender=ExamPassed)
def candidate_pass_exam(sender, instance, created, **kwargs):
    if created or not instance.processed:
        pr = ProcessExam()
        pr.delay(instance.id)
    else:
        if instance.processed and instance.points >= instance.exam.passing_grade:
            oracle = OracleHandler()
            vacancy = instance.exam.action.pipeline.vacancy
            cci = oracle.get_member_current_action_index(vacancy.company.contract_address, vacancy.uuid,
                                                         instance.candidate.contract_address)
            if cci == instance.exam.action.index:
                if not instance.exam.action.chain.approvable:
                    candidate_level_up.delay(vacancy.id, instance.candidate.id)


@receiver(pre_save, sender=AnswerForVerification)
def clear_older_answers(sender, instance, **kwargs):
    if instance.id is None:
        AnswerForVerification.objects.filter(question=instance.question).delete()


@receiver(post_save, sender=AnswerForVerification)
def process_verification(sender, instance, created, **kwargs):
    if created:
        va = VerifyAnswer()
        va.delay(instance.id)


@receiver(m2m_changed, sender=ActionExam.questions.through)
def recount_points(sender, instance, action, **kwargs):
    if action in ['post_add', 'post_remove', ]:
        max_points = sum([item.max_points for item in instance.questions.all()])
        if instance.passing_grade == 0:
            instance.passing_grade = max_points
        else:
            instance.passing_grade = max_points * (instance.passing_grade / instance.max_points)
        instance.max_points = max_points
        instance.save()
