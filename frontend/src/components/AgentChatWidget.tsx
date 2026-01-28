import { useState, useEffect, useRef } from 'react';

interface ChatMessage {
    id: string;
    role: 'user' | 'agent' | 'system';
    agent_type?: string;
    content: string;
    timestamp: string;
    actions?: Array<{
        label: string;
        action: string;
        payload?: any;
    }>;
}

interface AgentChatWidgetProps {
    caseId?: string;
    defaultOpen?: boolean;
}

/**
 * AgentChatWidget Component
 * 
 * Floating chat widget for conversational agent interaction.
 * Shows agent role indicators, message history, and action buttons.
 */
export function AgentChatWidget({ defaultOpen = false }: AgentChatWidgetProps) {
    const [isOpen, setIsOpen] = useState(defaultOpen);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (isOpen && messages.length === 0) {
            // Add welcome message
            setMessages([{
                id: 'welcome',
                role: 'agent',
                agent_type: 'intake_specialist',
                content: "Hi! I'm your GOATCRD Assistant. I can help you understand your loan options, answer questions about your scenarios, or guide you through the intake process. How can I help today?",
                timestamp: new Date().toISOString()
            }]);
        }
    }, [isOpen]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const sendMessage = async () => {
        if (!inputValue.trim()) return;

        const userMessage: ChatMessage = {
            id: `user-${Date.now()}`,
            role: 'user',
            content: inputValue,
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsLoading(true);

        try {
            // In production, would call backend chat endpoint
            // For now, simulate agent response
            await new Promise(resolve => setTimeout(resolve, 1000));

            const agentResponse = generateMockResponse(inputValue);
            setMessages(prev => [...prev, agentResponse]);
        } catch (error) {
            console.error('Failed to send message:', error);
            setMessages(prev => [...prev, {
                id: `error-${Date.now()}`,
                role: 'system',
                content: 'Sorry, I encountered an error. Please try again.',
                timestamp: new Date().toISOString()
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const generateMockResponse = (input: string): ChatMessage => {
        const lowerInput = input.toLowerCase();

        let response = '';
        let agentType = 'assistant';
        let actions: ChatMessage['actions'] = undefined;

        if (lowerInput.includes('scenario') || lowerInput.includes('option')) {
            agentType = 'scenario_analyst';
            response = "Based on your profile, I've identified 4 potential scenarios. The top option is a Prime Personal Loan at 8.9% APR with estimated monthly payments of $287. Would you like me to explain the differences between your options?";
            actions = [
                { label: 'Compare Top 3', action: 'compare_scenarios' },
                { label: 'View Details', action: 'view_scenario', payload: { id: 'scenario_1' } }
            ];
        } else if (lowerInput.includes('improve') || lowerInput.includes('better')) {
            agentType = 'coach';
            response = "I can suggest some ways to potentially improve your eligibility. Based on your current profile, reducing credit utilization below 30% could help. Keep in mind, I can only share general guidance—results are never guaranteed.";
            actions = [
                { label: 'Run Simulation', action: 'open_whatif' }
            ];
        } else if (lowerInput.includes('why') || lowerInput.includes('explain')) {
            agentType = 'explainer';
            response = "Let me explain that decision. The status was based on your current debt-to-income ratio of 42%, which exceeds the program's threshold of 40%. All factors are derived from verified data sources, including payroll verification.";
        } else if (lowerInput.includes('human') || lowerInput.includes('person')) {
            response = "I understand you'd like to speak with a human. Let me escalate this to our review team.";
            actions = [
                { label: 'Request Human Review', action: 'escalate_human' }
            ];
        } else {
            response = "I understand you're asking about your loan application. Could you tell me more specifically what you'd like to know? I can help with explaining scenarios, understanding reason codes, or guiding you through intake.";
        }

        return {
            id: `agent-${Date.now()}`,
            role: 'agent',
            agent_type: agentType,
            content: response,
            timestamp: new Date().toISOString(),
            actions
        };
    };

    const handleAction = (action: string, payload?: any) => {
        console.log('Action triggered:', action, payload);
        // Would handle navigation or API calls based on action
        setMessages(prev => [...prev, {
            id: `system-${Date.now()}`,
            role: 'system',
            content: `Action "${action}" triggered. This would navigate or execute the appropriate action.`,
            timestamp: new Date().toISOString()
        }]);
    };

    const getAgentAvatar = (agentType?: string): { emoji: string; color: string } => {
        const avatars: Record<string, { emoji: string; color: string }> = {
            'intake_specialist': { emoji: '📋', color: 'from-blue-500 to-cyan-500' },
            'scenario_analyst': { emoji: '📊', color: 'from-purple-500 to-pink-500' },
            'coach': { emoji: '🎯', color: 'from-green-500 to-emerald-500' },
            'explainer': { emoji: '💡', color: 'from-yellow-500 to-orange-500' },
            'compliance_reviewer': { emoji: '🔒', color: 'from-red-500 to-rose-500' },
            'assistant': { emoji: '🤖', color: 'from-gray-500 to-slate-500' }
        };
        return avatars[agentType || 'assistant'] || avatars.assistant;
    };

    if (!isOpen) {
        return (
            <button
                onClick={() => setIsOpen(true)}
                className="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 shadow-lg flex items-center justify-center text-2xl hover:scale-110 transition-transform z-50"
                aria-label="Open chat"
            >
                💬
            </button>
        );
    }

    return (
        <div className="fixed bottom-6 right-6 w-96 h-[500px] glass rounded-xl shadow-2xl flex flex-col z-50 border border-white/20">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-white/10">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                        🤖
                    </div>
                    <div>
                        <h3 className="text-white font-medium">GOATCRD Assistant</h3>
                        <p className="text-white/50 text-xs">Powered by AI agents</p>
                    </div>
                </div>
                <button
                    onClick={() => setIsOpen(false)}
                    className="text-white/50 hover:text-white p-1"
                >
                    ✕
                </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map(message => (
                    <div
                        key={message.id}
                        className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        {message.role === 'agent' && (
                            <div className={`w-8 h-8 rounded-full bg-gradient-to-br ${getAgentAvatar(message.agent_type).color} flex items-center justify-center text-sm mr-2 flex-shrink-0`}>
                                {getAgentAvatar(message.agent_type).emoji}
                            </div>
                        )}
                        <div className={`max-w-[80%] ${message.role === 'user'
                            ? 'bg-purple-500/30 rounded-2xl rounded-br-sm'
                            : message.role === 'system'
                                ? 'bg-gray-500/20 rounded-xl text-center'
                                : 'bg-white/10 rounded-2xl rounded-bl-sm'
                            } p-3`}>
                            <p className="text-white text-sm">{message.content}</p>
                            {message.actions && (
                                <div className="flex flex-wrap gap-2 mt-2">
                                    {message.actions.map((action, i) => (
                                        <button
                                            key={i}
                                            onClick={() => handleAction(action.action, action.payload)}
                                            className="bg-purple-500/30 hover:bg-purple-500/50 text-purple-200 text-xs px-3 py-1 rounded-full transition-colors"
                                        >
                                            {action.label}
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="flex justify-start">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-sm mr-2">
                            🤖
                        </div>
                        <div className="bg-white/10 rounded-2xl rounded-bl-sm p-3">
                            <div className="flex gap-1">
                                <span className="w-2 h-2 bg-white/50 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                                <span className="w-2 h-2 bg-white/50 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                                <span className="w-2 h-2 bg-white/50 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t border-white/10">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                        placeholder="Ask about your scenarios..."
                        className="flex-1 bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white placeholder-white/40 focus:outline-none focus:border-purple-500"
                    />
                    <button
                        onClick={sendMessage}
                        disabled={isLoading || !inputValue.trim()}
                        className="bg-purple-500 hover:bg-purple-600 disabled:opacity-50 text-white px-4 py-2 rounded-lg transition-colors"
                    >
                        Send
                    </button>
                </div>
                <p className="text-white/30 text-xs mt-2 text-center">
                    AI-assisted. Not financial advice. <button className="underline">Request human</button>
                </p>
            </div>
        </div>
    );
}

export default AgentChatWidget;
