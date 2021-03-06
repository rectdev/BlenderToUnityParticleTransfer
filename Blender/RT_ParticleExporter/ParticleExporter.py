import bpy
import os
import struct

class ParticleExporter():
    def __init__(self):
        self.reset()

    def get_particle_system(self, sceneObject):
        if sceneObject == None:
            self.reset()
            return False

        degp = bpy.context.evaluated_depsgraph_get()
        particle_systems = sceneObject.evaluated_get(degp).particle_systems

        if particle_systems == None or len(particle_systems) == 0:
            self.reset()
            return False

        self.__particle_system = particle_systems[0]
        self.__particle_count = len(self.__particle_system.particles)

        return True

    def export(self, output_path, filename, frame_start, frame_end, flip_yz):
        #create collections to collect the particle data
        particleDictionary = {}

        pState = []
        state = []
        lifeID = []
        name = []

        for i in range(0, self.__particle_count):
            pState.append('')
            state.append('')
            name.append('')
            lifeID.append(0)
            
        particles = self.__particle_system.particles

        #parse frames and collect data
        for f in range(frame_start, frame_end):
            bpy.context.scene.frame_set(f)

            for i in range(0, self.__particle_count):
                state[i] = particles[i].alive_state

                if pState[i] != state[i] and state[i] == 'ALIVE':
                    lifeID[i] += 1
                    name[i] = str(i) + "-" + str(lifeID[i])
                    particleDictionary[name[i]] = {}
                    particleDictionary[name[i]]["birth"] = particles[i].birth_time
                    particleDictionary[name[i]]["info"] = []

                if state[i] == 'ALIVE':
                    x = particles[i].location.x

                    if(flip_yz):
                        y = particles[i].location.z
                        z = particles[i].location.y
                    else:
                        y = particles[i].location.y
                        z = particles[i].location.z

                    info = {'x': x, 'y': y, 'z': z}

                    particleDictionary[name[i]]["info"].append(info)

                pState[i] = particles[i].alive_state

            print(f, end='\r')

        #save to file
        project_directory = os.path.dirname(bpy.data.filepath)
        os.chdir(project_directory)

        directory = os.path.dirname(output_path)
        directory = os.path.abspath(directory)
        print(directory)

        if not os.path.exists(directory):
            os.makedirs(directory)

        fullpath = os.path.join(output_path, filename + ".bpt")

        file = open(fullpath, "wb")
        file.write(struct.pack('<f', len(particleDictionary.keys())))
        file.write(struct.pack('<f', frame_start))
        file.write(struct.pack('<f', frame_end))

        for key in particleDictionary.keys():
            print(key, end='\r')

            length = len(particleDictionary[key]["info"])
            lenByte = struct.pack('<f', length)
            birthByte = struct.pack('<f', particleDictionary[key]["birth"])

            file.write(lenByte)
            file.write(birthByte)

            for i in range(length):
                if i < length:
                    info = particleDictionary[key]["info"][i]

                    x = struct.pack('<f', info["x"])
                    y = struct.pack('<f', info["y"])
                    z = struct.pack('<f', info["z"])

                file.write(x)
                file.write(y)
                file.write(z)

        file.close()

    def particle_count(self):
        return self.__particle_count
    
    def is_ready(self):
        return self.__particle_system != None

    def reset(self):
        self.__particle_system = None
        self.__particle_count = 0
