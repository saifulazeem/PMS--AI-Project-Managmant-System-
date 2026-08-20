from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, TeamMember, Project, Task, Comment, Notification
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,TeamMemberSerializer, ProjectSerializer, ProjectListSerializer,TaskSerializer,TaskListSerializer, CommentSerializer
)



# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def success(data, status_code=status.HTTP_200_OK):
    return Response({"success": True, "data": data}, status=status_code)

def error(msg, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({"success": False, "error": msg}, status=status_code)


# ═══════════════════════════════════════════════════════════════
# AUTH VIEWS
# ═══════════════════════════════════════════════════════════════

class RegisterView(APIView):
    """POST /api/auth/register/"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return success(
                {"message": "User registered successfully.", "user_id": user.id},
                status.HTTP_201_CREATED,
            )
        return error(serializer.errors)


class LoginView(APIView):
    """POST /api/auth/login/"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return success(serializer.validated_data)
        return error(serializer.errors, status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """POST /api/auth/logout/  — blacklists the refresh token"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data.get("refresh"))
            token.blacklist()
            return success({"message": "Logged out successfully."})
        except Exception as e:
            return error(str(e))


class MeView(APIView):
    """GET /api/auth/me/  — current user profile"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return success(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success(serializer.data)
        return error(serializer.errors)


# ═══════════════════════════════════════════════════════════════
# USER VIEWS
# ═══════════════════════════════════════════════════════════════

class UserListView(APIView):
    """GET /api/users/"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.filter(is_deleted=False)
        return success(UserSerializer(users, many=True).data)


class UserDetailView(APIView):
    """GET / PATCH / DELETE /api/users/<u_id>/"""
    permission_classes = [IsAuthenticated]

    def _get_user(self, id):
        try:
            return User.objects.get(id=id, is_deleted=False)
        except User.DoesNotExist:
            return None

    def get(self, request, id):
        user = self._get_user(id)
        if not user:
            return error("User not found.", status.HTTP_404_NOT_FOUND)
        return success(UserSerializer(user).data)

    def patch(self, request, id):
        user = self._get_user(id)
        if not user:
            return error("User not found.", status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success(serializer.data)
        return error(serializer.errors)

    def delete(self, request, id):
        user = self._get_user(id)
        if not user:
            return error("User not found.", status.HTTP_404_NOT_FOUND)
        user.soft_delete()
        return success({"message": "User deleted."})

# ═══════════════════════════════════════════════════════════════
# TEAM MEMBER VIEWS
# ═══════════════════════════════════════════════════════════════

class TeamMemberListCreateView(APIView):
    """GET /api/team-members/   POST /api/team-members/"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        members = TeamMember.objects.filter(is_deleted=0).order_by("name")
        return success(TeamMemberSerializer(members, many=True).data)

    def post(self, request):
        serializer = TeamMemberSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            member = serializer.save()
            return success(TeamMemberSerializer(member).data, status.HTTP_201_CREATED)
        return error(serializer.errors)


class TeamMemberDetailView(APIView):
    """GET / PATCH / DELETE /api/team-members/<id>/"""
    permission_classes = [IsAuthenticated]

    def _get_member(self, id):
        try:
            return TeamMember.objects.get(id=id, is_deleted=0)
        except TeamMember.DoesNotExist:
            return None

    def get(self, request, id):
        member = self._get_member(id)
        if not member:
            return error("Team member not found.", status.HTTP_404_NOT_FOUND)
        return success(TeamMemberSerializer(member).data)

    def patch(self, request, id):
        member = self._get_member(id)
        if not member:
            return error("Team member not found.", status.HTTP_404_NOT_FOUND)
        serializer = TeamMemberSerializer(member, data=request.data, partial=True,
                                          context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return success(serializer.data)
        return error(serializer.errors)

    def delete(self, request, id):
        member = self._get_member(id)
        if not member:
            return error("Team member not found.", status.HTTP_404_NOT_FOUND)
        member.is_deleted = 1
        member.save()
        return success({"message": "Team member deleted."})

# ═══════════════════════════════════════════════════════════════
# PROJECT VIEWS
# ═══════════════════════════════════════════════════════════════

class ProjectListCreateView(APIView):
    """GET /api/projects/   POST /api/projects/"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        projects = Project.objects.filter(is_deleted=False).order_by("-created_at")
        return success(ProjectListSerializer(projects, many=True).data)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            project = serializer.save()
            return success(ProjectSerializer(project).data, status.HTTP_201_CREATED)
        return error(serializer.errors)


class ProjectDetailView(APIView):
    """GET / PATCH / DELETE /api/projects/<p_id>/"""
    permission_classes = [IsAuthenticated]

    def _get_project(self, p_id):
        try:
            return Project.objects.get(p_id=p_id, is_deleted=False)
        except Project.DoesNotExist:
            return None

    def get(self, request, p_id):
        project = self._get_project(p_id)
        if not project:
            return error("Project not found.", status.HTTP_404_NOT_FOUND)
        return success(ProjectSerializer(project).data)

    def patch(self, request, p_id):
        project = self._get_project(p_id)
        if not project:
            return error("Project not found.", status.HTTP_404_NOT_FOUND)
        serializer = ProjectSerializer(project, data=request.data, partial=True,
                                       context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return success(serializer.data)
        return error(serializer.errors)

    def delete(self, request, p_id):
        project = self._get_project(p_id)
        if not project:
            return error("Project not found.", status.HTTP_404_NOT_FOUND)
        project.soft_delete()
        return success({"message": "Project deleted."})


class ProjectTasksView(APIView):
    """GET /api/projects/<p_id>/tasks/  — all tasks under a project"""
    permission_classes = [IsAuthenticated]

    def get(self, request, p_id):
        tasks = Task.objects.filter(p__p_id=p_id, is_deleted=False).order_by("-created_at")
        return success(TaskListSerializer(tasks, many=True).data)

# ═══════════════════════════════════════════════════════════════
# TASK VIEWS
# ═══════════════════════════════════════════════════════════════

class TaskListCreateView(APIView):
    """GET /api/tasks/   POST /api/tasks/"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(is_deleted=False).order_by("-created_at")
        # Optional filters via query params
        status_filter   = request.query_params.get("status")
        priority_filter = request.query_params.get("priority")
        assigned_to     = request.query_params.get("assign_to")
        project_id      = request.query_params.get("project")

        if status_filter:
            tasks = tasks.filter(status=status_filter)
        if priority_filter:
            tasks = tasks.filter(priority=priority_filter)
        if assigned_to:
            tasks = tasks.filter(assign_to__u_id=assigned_to)
        if project_id:
            tasks = tasks.filter(p__p_id=project_id)

        return success(TaskListSerializer(tasks, many=True).data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            task = serializer.save()
            return success(TaskSerializer(task).data, status.HTTP_201_CREATED)
        return error(serializer.errors)


class TaskDetailView(APIView):
    """GET / PATCH / DELETE /api/tasks/<t_id>/"""
    permission_classes = [IsAuthenticated]

    def _get_task(self, t_id):
        try:
            return Task.objects.get(t_id=t_id, is_deleted=False)
        except Task.DoesNotExist:
            return None

    def get(self, request, t_id):
        task = self._get_task(t_id)
        if not task:
            return error("Task not found.", status.HTTP_404_NOT_FOUND)
        return success(TaskSerializer(task).data)

    def patch(self, request, t_id):
        task = self._get_task(t_id)
        if not task:
            return error("Task not found.", status.HTTP_404_NOT_FOUND)
        serializer = TaskSerializer(task, data=request.data, partial=True,
                                    context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return success(serializer.data)
        return error(serializer.errors)

    def delete(self, request, t_id):
        task = self._get_task(t_id)
        if not task:
            return error("Task not found.", status.HTTP_404_NOT_FOUND)
        task.soft_delete()
        return success({"message": "Task deleted."})


class TaskCommentsView(APIView):
    """GET /api/tasks/<t_id>/comments/  — all comments on a task"""
    permission_classes = [IsAuthenticated]

    def get(self, request, t_id):
        comments = Comment.objects.filter(t__t_id=t_id).order_by("-created_at")
        return success(CommentSerializer(comments, many=True).data)

# ═══════════════════════════════════════════════════════════════
# COMMENT VIEWS
# ═══════════════════════════════════════════════════════════════

class CommentListCreateView(APIView):
    """GET /api/comments/   POST /api/comments/"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        comments = Comment.objects.all().order_by("-created_at")
        return success(CommentSerializer(comments, many=True).data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            comment = serializer.save()
            return success(CommentSerializer(comment).data, status.HTTP_201_CREATED)
        return error(serializer.errors)


class CommentDetailView(APIView):
    """GET / PATCH / DELETE /api/comments/<c_id>/"""
    permission_classes = [IsAuthenticated]

    def _get_comment(self, c_id):
        try:
            return Comment.objects.get(c_id=c_id)
        except Comment.DoesNotExist:
            return None

    def get(self, request, c_id):
        comment = self._get_comment(c_id)
        if not comment:
            return error("Comment not found.", status.HTTP_404_NOT_FOUND)
        return success(CommentSerializer(comment).data)

    def patch(self, request, c_id):
        comment = self._get_comment(c_id)
        if not comment:
            return error("Comment not found.", status.HTTP_404_NOT_FOUND)
        if comment.u != request.user:
            return error("You can only edit your own comments.", status.HTTP_403_FORBIDDEN)
        serializer = CommentSerializer(comment, data=request.data, partial=True,
                                       context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return success(serializer.data)
        return error(serializer.errors)

    def delete(self, request, c_id):
        comment = self._get_comment(c_id)
        if not comment:
            return error("Comment not found.", status.HTTP_404_NOT_FOUND)
        if comment.u != request.user:
            return error("You can only delete your own comments.", status.HTTP_403_FORBIDDEN)
        comment.delete()
        return success({"message": "Comment deleted."})


class CommentPinView(APIView):
    """PATCH /api/comments/<c_id>/pin/  — toggle pin"""
    permission_classes = [IsAuthenticated]

    def patch(self, request, c_id):
        try:
            comment = Comment.objects.get(c_id=c_id)
        except Comment.DoesNotExist:
            return error("Comment not found.", status.HTTP_404_NOT_FOUND)
        comment.pin = not comment.pin
        comment.save()
        return success({"pinned": comment.pin})


# ═══════════════════════════════════════════════════════════════
# NOTIFICATION VIEWS
# ═══════════════════════════════════════════════════════════════

class NotificationListView(APIView):
    """GET /api/notifications/  — current user's notifications"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(
            u=request.user, is_deleted__isnull=True
        ).order_by("-created_at")
        return success(NotificationSerializer(notifications, many=True).data)


class NotificationDetailView(APIView):
    """GET /api/notifications/<n_id>/"""
    permission_classes = [IsAuthenticated]

    def get(self, request, n_id):
        try:
            notification = Notification.objects.get(n_id=n_id, u=request.user)
        except Notification.DoesNotExist:
            return error("Notification not found.", status.HTTP_404_NOT_FOUND)
        return success(NotificationSerializer(notification).data)


class NotificationMarkReadView(APIView):
    """PATCH /api/notifications/<n_id>/read/"""
    permission_classes = [IsAuthenticated]

    def patch(self, request, n_id):
        try:
            notification = Notification.objects.get(n_id=n_id, u=request.user)
        except Notification.DoesNotExist:
            return error("Notification not found.", status.HTTP_404_NOT_FOUND)
        notification.mark_as_read()
        return success({"message": "Notification marked as read."})


class NotificationMarkAllReadView(APIView):
    """PATCH /api/notifications/read-all/"""
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        now = timezone.now()
        Notification.objects.filter(
            u=request.user, is_read=False
        ).update(is_read=True, read_at=now)
        return success({"message": "All notifications marked as read."})


class NotificationDeleteView(APIView):
    """DELETE /api/notifications/<n_id>/"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, n_id):
        try:
            notification = Notification.objects.get(n_id=n_id, u=request.user)
        except Notification.DoesNotExist:
            return error("Notification not found.", status.HTTP_404_NOT_FOUND)
        notification.is_deleted = timezone.now()
        notification.save()
        return success({"message": "Notification deleted."})

