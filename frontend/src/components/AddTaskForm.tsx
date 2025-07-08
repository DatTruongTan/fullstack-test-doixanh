import { useState } from 'react';
import type { FormEvent } from 'react';
import type { TaskCreate } from '../types';
import { useToast } from '../contexts/ToastContext';

const isSessionExpiredError = (err: any): boolean => {
    return err?.response?.status === 401;
};

interface AddTaskFormProps {
    onAddTask: (task: TaskCreate) => Promise<boolean>;
}

const AddTaskForm = ({ onAddTask }: AddTaskFormProps) => {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [priority, setPriority] = useState<'low' | 'normal' | 'high'>('normal');
    const [dueDate, setDueDate] = useState<string>(getTodayDate());
    const [isSubmitting, setIsSubmitting] = useState(false);

    const { addToast } = useToast();

    function getTodayDate() {
        const today = new Date();
        return today.toISOString().split('T')[0];
    }

    function isValidDueDate(date: string): boolean {
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const selectedDate = new Date(date);
        selectedDate.setHours(0, 0, 0, 0);

        return selectedDate >= today;
    }

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();

        if (!title.trim()) {
            addToast('Title is required', 'error');
            return;
        }

        if (!isValidDueDate(dueDate)) {
            addToast('Due date cannot be in the past', 'warning');
            return;
        }

        setIsSubmitting(true);

        try {
            const success = await onAddTask({
                title,
                description,
                due_date: new Date(dueDate).toISOString(),
                priority
            });

            if (success) {
                setTitle('');
                setDescription('');
                setPriority('normal');
                setDueDate(getTodayDate());
            }
        } catch (err) {
            console.error(err);
            if (!isSessionExpiredError(err)) {
                addToast('Failed to add task. Please try again.', 'error');
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="add-task-form">
            <h2>Add New Task</h2>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="task-title">Title *</label>
                    <input
                        id="task-title"
                        type="text"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="Enter task title"
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="task-description">Description (optional)</label>
                    <textarea
                        id="task-description"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="Enter task description"
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="task-due-date">Due Date *</label>
                    <input
                        id="task-due-date"
                        type="date"
                        value={dueDate}
                        onChange={(e) => setDueDate(e.target.value)}
                        min={getTodayDate()}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="task-priority">Priority</label>
                    <select
                        id="task-priority"
                        value={priority}
                        onChange={(e) => setPriority(e.target.value as 'low' | 'normal' | 'high')}
                    >
                        <option value="low">Low</option>
                        <option value="normal">Normal</option>
                        <option value="high">High</option>
                    </select>
                </div>
                <button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? 'Adding...' : 'Add Task'}
                </button>
            </form>
        </div>
    );
};

export default AddTaskForm; 