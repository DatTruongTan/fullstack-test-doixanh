import { useState } from 'react';
import type { Task } from '../types';
import { useToast } from '../contexts/ToastContext';

const isSessionExpiredError = (err: any): boolean => {
    return err?.response?.status === 401;
};

interface TaskItemProps {
    task: Task;
    onDelete: (id: number) => Promise<boolean>;
    onUpdate: (id: number, updates: {
        title?: string;
        description?: string;
        completed?: boolean;
        due_date?: string;
        priority?: 'low' | 'normal' | 'high';
    }) => Promise<boolean>;
    onCheckboxChange?: (id: number, checked: boolean) => void;
    isSelected?: boolean;
}

const TaskItem = ({ task, onDelete, onUpdate, onCheckboxChange, isSelected = false }: TaskItemProps) => {
    const [isEditing, setIsEditing] = useState(false);
    const [showDetails, setShowDetails] = useState(false);
    const [title, setTitle] = useState(task.title);
    const [description, setDescription] = useState(task.description);
    const [dueDate, setDueDate] = useState(new Date(task.due_date).toISOString().split('T')[0]);
    const [priority, setPriority] = useState<'low' | 'normal' | 'high'>(task.priority);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const { addToast } = useToast();

    function getTodayDate() {
        const today = new Date();
        return today.toISOString().split('T')[0];
    }

    function formatDate(dateString: string) {
        const date = new Date(dateString);
        return date.toLocaleDateString();
    }

    const handleToggleComplete = async () => {
        try {
            const status = !task.completed ? 'completed' : 'active';
            const success = await onUpdate(task.id, { completed: !task.completed });
            if (success) {
                addToast(`Task marked as ${status}`, 'info');
            }
        } catch (err) {
            console.error(err);
            if (!isSessionExpiredError(err)) {
                addToast('Failed to update task status', 'error');
            }
        }
    };

    const handleSave = async () => {
        if (!title.trim()) {
            addToast('Title is required', 'error');
            return;
        }

        setIsSubmitting(true);

        try {
            const success = await onUpdate(task.id, {
                title,
                description,
                due_date: new Date(dueDate).toISOString(),
                priority
            });

            if (success) {
                setIsEditing(false);
                setShowDetails(false);
            }
        } catch (err) {
            console.error(err);
            if (!isSessionExpiredError(err)) {
                addToast('Failed to update task', 'error');
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleCancel = () => {
        setTitle(task.title);
        setDescription(task.description);
        setDueDate(new Date(task.due_date).toISOString().split('T')[0]);
        setPriority(task.priority);
        setIsEditing(false);
    };

    const handleDelete = async () => {
        setIsSubmitting(true);

        try {
            const success = await onDelete(task.id);
            if (success && showDetails) {
                setShowDetails(false);
            }
        } catch (err) {
            console.error(err);
            if (!isSessionExpiredError(err)) {
                addToast('Failed to delete task', 'error');
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleSelect = () => {
        if (onCheckboxChange) {
            onCheckboxChange(task.id, !isSelected);
        }
    };

    const getPriorityColor = (priority: string) => {
        switch (priority) {
            case 'high': return 'priority-high';
            case 'low': return 'priority-low';
            default: return 'priority-normal';
        }
    };

    if (showDetails || isEditing) {
        return (
            <div className={`task-detail-view ${task.completed ? 'completed' : ''} ${isSelected ? 'selected' : ''}`}>
                <div className="task-detail-header">
                    <h3>{isEditing ? 'Edit Task' : 'Task Details'}</h3>
                </div>

                <div className="task-detail-content">
                    <div className="form-group">
                        <label>Title</label>
                        <input
                            type="text"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            placeholder="Task title"
                            readOnly={!isEditing}
                            className={!isEditing ? 'readonly' : ''}
                        />
                    </div>

                    <div className="form-group">
                        <label>Description</label>
                        <textarea
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            placeholder="No description"
                            readOnly={!isEditing}
                            className={!isEditing ? 'readonly' : ''}
                        />
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label>Due Date</label>
                            <input
                                type="date"
                                value={dueDate}
                                onChange={(e) => setDueDate(e.target.value)}
                                min={isEditing ? getTodayDate() : undefined}
                                readOnly={!isEditing}
                                className={!isEditing ? 'readonly' : ''}
                            />
                        </div>

                        <div className="form-group">
                            <label>Priority</label>
                            {isEditing ? (
                                <select
                                    value={priority}
                                    onChange={(e) => setPriority(e.target.value as 'low' | 'normal' | 'high')}
                                >
                                    <option value="low">Low</option>
                                    <option value="normal">Normal</option>
                                    <option value="high">High</option>
                                </select>
                            ) : (
                                <div className={`priority-badge ${getPriorityColor(priority)}`}>
                                    {priority.charAt(0).toUpperCase() + priority.slice(1)}
                                </div>
                            )}
                        </div>

                        <div className="form-group">
                            <label>Status</label>
                            <div className="status-toggle">
                                <label className="toggle">
                                    <input
                                        type="checkbox"
                                        checked={task.completed}
                                        onChange={handleToggleComplete}
                                    />
                                    <span className="toggle-label">
                                        {task.completed ? 'Completed' : 'Active'}
                                    </span>
                                </label>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="task-detail-footer">
                    {isEditing ? (
                        <>
                            <button
                                onClick={handleSave}
                                className="primary-button"
                                disabled={isSubmitting}
                            >
                                {isSubmitting ? 'Saving...' : 'Save'}
                            </button>
                            <button
                                onClick={handleCancel}
                                className="secondary-button"
                                disabled={isSubmitting}
                            >
                                Cancel
                            </button>
                        </>
                    ) : (
                        <>
                            <button
                                onClick={() => setIsEditing(true)}
                                className="primary-button"
                                disabled={isSubmitting}
                            >
                                Edit
                            </button>
                            <button
                                onClick={handleDelete}
                                className="danger-button"
                                disabled={isSubmitting}
                            >
                                {isSubmitting ? 'Removing...' : 'Remove'}
                            </button>
                            <button
                                onClick={() => setShowDetails(false)}
                                className="secondary-button"
                                disabled={isSubmitting}
                            >
                                Close
                            </button>
                        </>
                    )}
                </div>
            </div>
        );
    }

    return (
        <div className={`task-item ${task.completed ? 'completed' : ''} ${isSelected ? 'selected' : ''}`} onClick={handleSelect}>
            <div className="task-content">
                <div className="task-header">
                    <h3 className={task.completed ? 'completed-text' : ''}>{task.title}</h3>
                    <div className={`priority-badge ${getPriorityColor(task.priority)}`}>
                        {priority.charAt(0).toUpperCase() + priority.slice(1)}
                    </div>
                </div>
                <div className="task-date">
                    Due: {formatDate(task.due_date)}
                </div>
            </div>
            <div className="task-actions">
                <button
                    onClick={(e) => {
                        e.stopPropagation();
                        handleToggleComplete();
                    }}
                    className={`done-button ${task.completed ? 'done' : ''}`}
                >
                    {task.completed ? 'Completed' : 'Mark Done'}
                </button>
                <button
                    onClick={(e) => {
                        e.stopPropagation();
                        setShowDetails(true);
                    }}
                    className="detail-button"
                >
                    Detail
                </button>
                <button
                    onClick={(e) => {
                        e.stopPropagation();
                        handleDelete();
                    }}
                    className="remove-button"
                >
                    Remove
                </button>
            </div>
        </div>
    );
};

export default TaskItem; 