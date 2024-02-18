
from ciocore.validator import Validator
import logging
import bpy

logger = logging.getLogger(__name__)
SAMPLES = 256

class ValidateScoutFrames(Validator):
    def run(self, _):
        """
        Add a validation warning for a potentially costly scout frame configuration.
        """
        try:
            kwargs = self._submitter
            use_scout_frames = kwargs.get("use_scout_frames")
            chunk_size = kwargs.get("chunk_size")

            if chunk_size > 1 and use_scout_frames:
                msg = "You have chunking set higher than 1."
                msg += " This can cause more scout frames to be rendered than you might expect."
                self.add_warning(msg)

        except Exception as e:
            logger.debug("ValidateScoutFrames: {}".format(e))
"""
class ValidateMAXSamples(Validator):
    def run(self, _):
        # Add a validation warning for a high Max Samples value
        try:
            scene = bpy.context.scene
            max_samples = scene.cycles.samples
            if max_samples > SAMPLES:
                msg = "You've increased the Max Samples beyond 256. "
                msg += "While having more samples generally improves results, "
                msg += "there's a point where the returns diminish. It's essential to perform test renders "
                msg += "to find the optimal sample count, balancing render time and quality. "
                msg += "Typically, a Max Samples value between 64 and 256, with Min Samples between 0 and 32 when using denoise, "
                msg += "suffices for most scenes. To adjust these settings, navigate to Render Properties > Sampling > Render."

                self.add_warning(msg)

        except Exception as e:
            logger.debug("ValidateResolvedChunkSize: {}".format(e))
"""
class ValidateResolvedChunkSize(Validator):
    def run(self, _):
        """
        Add a validation warning for a potentially costly scout frame configuration.
        """
        try:
            kwargs = self._submitter
            chunk_size = kwargs.get("chunk_size", None)
            resolved_chunk_size = kwargs.get("resolved_chunk_size", None)
            if chunk_size and resolved_chunk_size:
                chunk_size = int(chunk_size)
                resolved_chunk_size = int(resolved_chunk_size)

                if resolved_chunk_size > chunk_size:
                    msg = "The number of frames per task has been automatically increased to maintain " \
                          "a total task count below 800. If you have a time-sensitive deadline and require each frame to be " \
                          "processed on a dedicated instance, you might want to consider dividing the frame range into smaller " \
                          "portions. " \
                          "Alternatively, feel free to reach out to Conductor Customer Support for assistance."
                    self.add_warning(msg)

        except Exception as e:
            logger.debug("ValidateResolvedChunkSize: {}".format(e))

class ValidateSaveSceneBeforeSubmission(Validator):
    def run(self, _):
        """
        Add a validation warning for a using CPU rendering with Eevee.
        """
        try:
            if bpy.data.is_dirty:
                msg = "The scene contains unsaved modifications. "
                msg += "To include these recent changes in your submission, select 'Save Scene and Continue Submission'. "
                msg += "Be aware that saving the scene now may result in additional upload time, "
                msg += "if the scene is already uploaded to the render farm. "
                msg += "If you prefer to proceed without incorporating these changes, choose 'Continue Submission'"
                self.add_warning(msg)

        except Exception as e:
            logger.debug("ValidateSaveSceneBeforeSubmission: {}".format(e))

class ValidateGPURendering(Validator):
    def run(self, _):
        """
        Add a validation warning for a using CPU rendering with Eevee.
        """
        try:
            kwargs = self._submitter
            instance_type_family = kwargs.get("instance_type")
            driver_software = kwargs.get("render_software")
            if "eevee" in driver_software.lower() and "cpu" in instance_type_family.lower():
                msg = "CPU rendering is selected."
                msg += " We strongly recommend selecting GPU rendering when using Blender’s render engine, Eevee."
                self.add_warning(msg)
        except Exception as e:
            logger.debug("ValidateGPURendering: {}".format(e))



# Implement more validators here
####################################


def run(kwargs):
    errors, warnings, notices = [], [], []

    er, wn, nt = _run_validators(kwargs)

    errors.extend(er)
    warnings.extend(wn)
    notices.extend(nt)

    return errors, warnings, notices

def _run_validators(kwargs):


    validators = [plugin(kwargs) for plugin in Validator.plugins()]
    logger.debug("Validators: %s", validators)
    for validator in validators:
        validator.run(kwargs)

    errors = list(set.union(*[validator.errors for validator in validators]))
    warnings = list(set.union(*[validator.warnings for validator in validators]))
    notices = list(set.union(*[validator.notices for validator in validators]))
    return errors, warnings, notices


