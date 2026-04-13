import torch
import torch.nn as nn


class ActorNetworkWithEncoder(nn.Module):
    def __init__(
            self,
            num_actor_obs,
            num_critic_obs,
            num_actions,
            num_encoder_obs,
            num_encoder_out,
            actor_hidden_dims=None,
            critic_hidden_dims=None,
            encoder_hidden_dims=None,
            activation="elu",
            init_noise_std=1.0,
            **kwargs,
    ):
        if critic_hidden_dims is None:
            critic_hidden_dims = [512, 256, 256]
        if actor_hidden_dims is None:
            actor_hidden_dims = [512, 256, 256]
        if encoder_hidden_dims is None:
            encoder_hidden_dims = [128, 128]

        if kwargs:
            print("ActorCritic.__init__ got unexpected arguments, which will be ignored: " + str(list(kwargs.keys())))
        super().__init__()

        activation = get_activation(activation)

        mlp_input_dim_a = num_actor_obs
        mlp_input_dim_c = num_critic_obs
        mlp_input_dim_e = num_encoder_obs
        mlp_output_dim_e = num_encoder_out

        # Encoder
        encoder_layers = []
        encoder_layers.append(nn.Linear(mlp_input_dim_e, encoder_hidden_dims[0]))
        encoder_layers.append(activation)
        for l in range(len(encoder_hidden_dims)):
            if l == len(encoder_hidden_dims) - 1:
                encoder_layers.append(nn.Linear(encoder_hidden_dims[l], mlp_output_dim_e))
            else:
                encoder_layers.append(nn.Linear(encoder_hidden_dims[l], encoder_hidden_dims[l + 1]))
                encoder_layers.append(activation)
        self.encoder = nn.Sequential(*encoder_layers)

        print(f"Encoder MLP: {self.encoder}")

        # Policy
        actor_layers = []
        actor_layers.append(nn.Linear(mlp_input_dim_a, actor_hidden_dims[0]))
        actor_layers.append(activation)

        for l in range(len(actor_hidden_dims)):
            if l == len(actor_hidden_dims) - 1:
                actor_layers.append(nn.Linear(actor_hidden_dims[l], num_actions))
            else:
                actor_layers.append(nn.Linear(actor_hidden_dims[l], actor_hidden_dims[l + 1]))
                actor_layers.append(activation)

        self.actor = nn.Sequential(*actor_layers)

        # Value function
        critic_layers = []
        critic_layers.append(nn.Linear(mlp_input_dim_c, critic_hidden_dims[0]))
        critic_layers.append(activation)

        for l in range(len(critic_hidden_dims)):
            if l == len(critic_hidden_dims) - 1:
                critic_layers.append(nn.Linear(critic_hidden_dims[l], 1))
            else:
                critic_layers.append(nn.Linear(critic_hidden_dims[l], critic_hidden_dims[l + 1]))
                critic_layers.append(activation)

        self.critic = nn.Sequential(*critic_layers)

        print(f"Actor MLP: {self.actor}")
        print(f"Critic MLP: {self.critic}")

        self.std = nn.Parameter(init_noise_std * torch.ones(num_actions))

    def act_inference(self, observations):
        actions_mean = self.actor(observations)
        return actions_mean

    def encode_inference(self, encoder_observations):
        observation_mean = self.encoder(encoder_observations)
        return observation_mean


def get_activation(act_name):
    if act_name == "elu":
        return nn.ELU()
    elif act_name == "selu":
        return nn.SELU()
    elif act_name == "relu":
        return nn.ReLU()
    elif act_name == "crelu":
        return nn.ReLU()
    elif act_name == "lrelu":
        return nn.LeakyReLU()
    elif act_name == "tanh":
        return nn.Tanh()
    elif act_name == "sigmoid":
        return nn.Sigmoid()
    else:
        print("invalid activation function!")
        return None
