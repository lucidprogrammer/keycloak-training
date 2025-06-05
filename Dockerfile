FROM python:3.11-slim
WORKDIR /app
RUN pip install flask authlib requests
COPY app.py .
COPY internal-portal/ /app/internal-portal/
COPY external-portal/ /app/external-portal/
COPY admin-dashboard/ /app/admin-dashboard/
EXPOSE 5000
CMD ["python", "app.py", "--portal=internal"]