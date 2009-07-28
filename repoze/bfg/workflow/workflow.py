from zope.interface import implements
from zope.interface import classImplements

from repoze.bfg.security import has_permission
from repoze.bfg.workflow.statemachine import StateMachineError
from repoze.bfg.workflow.interfaces import IWorkflow
from repoze.bfg.workflow.interfaces import IWorkflowFactory

class Workflow:
    classImplements(IWorkflowFactory)
    implements(IWorkflow)
    def __init__(self, context, machine):
        self.context = context
        self.machine = machine # r.b.workflow.statemachine.StateMachine instance

    def execute(self, request, transition_name):
        def permission_guard(context, transition):
            permission = transition.get('permission')
            if request is not None and permission is not None:
                if not has_permission(permission, context, request):
                    raise StateMachineError(
                        '%s permission required for transition %r' % (
                        permission, transition_name)
                        )
        self.machine.execute(self.context, transition_name,
                             guards=(permission_guard,))

    def transitions(self, request, from_state=None):
        info = self.machine.transitions(self.context, from_state)
        return [ thing for thing in info if
                 has_permission(thing.get('permission', None),
                                self.context, request) ]
