from uagents import Agent, Context, Protocol, Model, Bureau

# Define message models
class SymptomMessage(Model):
    text: str

class DiagnosisMessage(Model):
    text: str

# Define agents with unique ports
triage_agent = Agent(name="TriageAgent", port=8000)
action_agent = Agent(name="ActionAgent", port=8001)

# Define protocol for communication
triage_protocol = Protocol("TriageProtocol")

@triage_protocol.on_message(model=SymptomMessage)
async def handle_symptoms(ctx: Context, sender: str, msg: SymptomMessage):
    ctx.logger.info(f"Received symptoms from {sender}: {msg.text}")
    diagnosis = DiagnosisMessage(text=f"Analyzed: {msg.text} -> Suggest rest.")
    await ctx.send(action_agent.address, diagnosis)

@triage_protocol.on_message(model=DiagnosisMessage)
async def handle_action(ctx: Context, sender: str, msg: DiagnosisMessage):
    ctx.logger.info(f"Received diagnosis from {sender}: {msg.text}")
    action = "Action: Schedule doctor if needed."
    ctx.logger.info(action)

# Attach protocol to agents
triage_agent.include(triage_protocol)
action_agent.include(triage_protocol)

# Trigger single test message on startup
@triage_agent.on_event("startup")
async def send_test_symptom(ctx: Context):
    ctx.logger.info("TriageAgent startup: Sending test symptom message")
    await ctx.send(triage_agent.address, SymptomMessage(text="fever and cough"))
    ctx.logger.info("Sent test symptom.")

# Use Bureau to run both agents
bureau = Bureau()
bureau.add(triage_agent)
bureau.add(action_agent)

if __name__ == "__main__":
    bureau.run()