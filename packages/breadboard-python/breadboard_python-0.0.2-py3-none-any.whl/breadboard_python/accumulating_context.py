
from breadboard_python.main import Board, Field, SchemaObject, List, AttrDict
import json
from typing import Optional, Union

from breadboard_python.import_node import require
Core = require("@google-labs/core-kit")
Templates = require("@google-labs/template-kit")
Palm = require("@google-labs/palm-kit")

class InputSchema(SchemaObject):
  text: str = Field(title="User", descrption="Type here to chat with the assistant", required=True)

class AccumulatingContext(Board):
  title = "Accumulating Context (Python)"
  description = 'An example of a board that implements a multi-turn experience: a very simple chat bot that accumulates context of the conversations. Tell it "I am hungry" or something like this and then give simple replies, like "bbq". It should be able to infer what you\'re asking for based on the conversation context. All replies are pure hallucinations, but should give you a sense of how a Breadboard API endpoint for a board with cycles looks like.'
  version = "0.0.1"

  def __init__(self):
    self.prompt = Templates.promptTemplate(
      id="assistant",
      tempalte="This is a conversation between a friendly assistant and their user. You are the assistant and your job is to try to be helpful, empathetic, and fun.\n{{context}}\n\n== Current Conversation\nuser: {{question}}\nassistant:",
      context="",
    )
    self.conversationMemory = Core.append(
      accumulator="\n== Conversation History",
    )

  def describe(self, input):
    

// Use the `append` node to accumulate the conversation history.
// Populate it with initial context.
const conversationMemory = core.append({
  accumulator: "\n== Conversation History",
  $id: "conversationMemory",
});
// Wire memory to accumulate: loop it to itself.
conversationMemory.wire("accumulator->", conversationMemory);

core.passthrough({ $id: "start" }).wire(
  "->",
  input
    .wire(
      "text->question",
      prompt.wire(
        "prompt->text",
        palm
          .generateText({ $id: "generator" })
          .wire("<-PALM_KEY.", core.secrets({ keys: ["PALM_KEY"] }))
          .wire(
            "completion->assistant",
            conversationMemory.wire("accumulator->context", prompt)
          )
          .wire(
            "completion->text",
            board
              .output({
                $id: "assistantResponse",
                schema: {
                  type: "object",
                  properties: {
                    text: {
                      type: "string",
                      title: "Assistant",
                      description:
                        "Assistant's response in the conversation with the user",
                    },
                  },
                  required: ["text"],
                },
              })
              .wire("->", input)
          )
      )
    )
    .wire("text->user", conversationMemory)
);

export default board;
