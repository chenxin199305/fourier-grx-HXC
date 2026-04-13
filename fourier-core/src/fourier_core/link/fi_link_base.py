class LinkBase:
    def __init__(self, length=None, mass=None, cog=None, inertia=None):
        if length is None:
            length = 0
        self.length = length

        if mass is None:
            mass = 0
        self.mass = mass

        if cog is None:
            cog = [0, 0, 0]
        self.cog = cog

        if inertia is None:
            inertia = [0, 0, 0]
        self.inertia = inertia
